<?php
	error_reporting(E_ALL | E_WARNING | E_NOTICE);
	ini_set('display_errors', TRUE);


	require "HTTP/Request2.php";	
	include("simple_html_dom.php"); //Import DOM parser

	header("Location: text_sent.html");

	echo "<html></html>";  // - Tell the browser there the page is done
	flush();               // - Make sure all buffers are flushed
	ob_flush();            // - Make sure all buffers are flushed

	$sourceAirport =  strtoupper($_POST["from"]);
	$destinationAirport = strtoupper($_POST["to"]);
	#$flightNumberInput = $_POST["flightNumber"];
	$priorityCode = $_POST["priorityCode"];
	$priorityDate = $_POST["priorityDate"];
	$selectedDate = $_POST["date"];
	$selectedTime = $_POST["depart_time"];
	$phoneToText = $_POST["phone_digits"];

	#if ($_POST["travelMethod"] == 'All Flights')
	#	$direct_or_all_flights = '12N';
	#else
	#	$direct_or_all_flights = 'D';

	$homeURL = "https://connect.delta.com/my.logon.php3?check=1";
	$activationURL = "https://connect.delta.com/my.activation.php3";
	$mainPageURL = "https://connect.delta.com/f5-w-68747470733a2f2f64656c746170617373706f72742e64656c74612e636f6d$$/";
	$refreshURL = "https://connect.delta.com/vdesk/intranets/provision.php3?intranetwebtop=1";
	$flightsURL = "https://connect.delta.com/f5-w-68747470733a2f2f74726176656c2e64656c74612e636f6d$$/etb/nonRevenueSearch.do?search=getflights&travelWarningPresent=null";
	$standbyListURL = "https://connect.delta.com/f5-w-68747470733a2f2f74726176656c2e64656c74612e636f6d$$/etb/dwr/call/plaincall/Popup.getInclude.dwr?F5CH=I";

	$html = file_get_html($homeURL);
			
	$loginFormData = array();

	// Store all inputs in array 
	foreach($html->find("input") as $element) 
	{
		$loginFormData[$element->name] = $element->value;
	}

	$loginFormData["username"] = "081714800";
	$loginFormData["password"] = "dlfor2me";

	//			LOGIN REQUEST				//

	$loginRequest = new HTTP_Request2($activationURL, HTTP_Request2::METHOD_POST);
	$loginRequest->addPostParameter($loginFormData);
	$loginRequest->setConfig(array(
	    'ssl_verify_peer'   => FALSE,
	    'ssl_verify_host'   => FALSE
	));

	$loginResponse = $loginRequest->send();

	//echo $loginResponse->getBody();



	//			 MAIN PAGE REQUEST				//
	$refreshRequest = new HTTP_Request2($refreshURL, HTTP_Request2::METHOD_GET);
	$mainPageRequest = new HTTP_Request2($mainPageURL, HTTP_Request2::METHOD_POST);
	$refreshRequest->setConfig(array(
	    'ssl_verify_peer'   => FALSE,
	    'ssl_verify_host'   => FALSE
	));
	$mainPageRequest->setConfig(array(
	    'ssl_verify_peer'   => FALSE,
	    'ssl_verify_host'   => FALSE
	));

	foreach ($loginResponse->getCookies() as $arCookie) 
	{
		$refreshRequest->addCookie($arCookie["name"], $arCookie["value"]); 
		$mainPageRequest->addCookie($arCookie["name"], $arCookie["value"]);
	} 

	$refreshResponse = $refreshRequest->send();
	
	$timeStamp = time() . "_0_3600";
	
	$mainPageFormData = array(
		"Z" => "0,0"
	);

	$mainPageRequest->addPostParameter($mainPageFormData);
	$mainPageResponse = $mainPageRequest->send();



	//		Flight Search Request 		//


	$flightSearchRequest = new HTTP_Request2($flightsURL, HTTP_Request2::METHOD_POST);
	$flightSearchRequest->setConfig(array(
	    'ssl_verify_peer'   => FALSE,
	    'ssl_verify_host'   => FALSE
	));

	foreach ($mainPageResponse->getCookies() as $c)
	{
		$flightSearchRequest->addCookie($c["name"], $c["value"]);
	}

	$flightPostData = array(

		'nextLeaveDate'			=>    '',          
		'prevLeaveDate'                 =>    '',
		'flightNextLeaveDate'           =>    '',
		'flightPrevLeaveDate'           =>    '',
		'nextReturnDate'                =>    '',
		'prevReturnDate'                =>    '',
		'activeMenu'			=>    'nonRevenue',
		'relevantYear'                  =>    '',
		'fromPage'                      =>    '',
		'listType'                      =>    '',
		'selectedInfantInArmsSsr'       =>    '',
		'searchType'			=>    'schedule',
		'fromAirport'			=>    $sourceAirport,
		'toAirport'			=>    $destinationAirport,
		'viaAirport'			=>    '',
		'tripWay'			=>    '12N',
		'leaveDate'			=>    $selectedDate,
		'leaveTime'			=>    $travelMethod,	//12N for all flights , D for direct only
		'flightNumber'			=>    '',
		'flightFromAirport'             =>    '',
		'flightToAirport'               =>    '',
		'flightLeaveDate'		=>    $selectedDate,
		'selectFlightOut'		=>    '1'
	);

	$flightSearchRequest->addPostParameter($flightPostData);
	$flightResponse = $flightSearchRequest->send();

	$flightsHTML = new simple_html_dom();
	$flightsHTML->load($flightResponse->getBody());

	$totalFlightsCount = 0;

	foreach ($flightsHTML->find('img[alt]') as $element)
	{
		if ($element->alt == 'show flight load information')
			$totalFlightsCount++;

	}
		

	$timeCounter = 0;
	preg_match_all('/>(1[0-2]|0?[1-9]):([0-5]?[0-9])(am|pm)/i', $flightResponse->getBody(), $timeMatches);
	
	$mainFlightPage = uniqid("mainFlightPage_");
	$allFlightInformation = uniqid('allFlights_');

	$mainFlightPage = $mainFlightPage . ".txt";
	$allFlightInformation = $allFlightInformation . ".txt";

	#$mainFlightPage = 'mainFlightPage.txt';
	#$allFlightInformation = 'allFlights.txt';

	file_put_contents($mainFlightPage, $flightResponse->getBody(), FILE_APPEND);

	

	//		SHOW STANDBYLIST REQUEST		//
	for($flightIndex=0; $flightIndex < $totalFlightsCount; $flightIndex++)
	{ 
		$showPopUpsRequest = new HTTP_Request2($standbyListURL, HTTP_Request2::METHOD_POST);
		$showPopUpsRequest->setConfig(array(
		    'ssl_verify_peer'   => FALSE,
		    'ssl_verify_host'   => FALSE
		));

		foreach ($mainPageResponse->getCookies() as $c)
		{
			$showPopUpsRequest->addCookie($c["name"], $c["value"]);
		}



		$payloadRequest = array(
			'callCount' => '1',
			'windowName' => '',
			'c0-scriptName' => 'Popup',
			'c0-methodName' => 'getInclude',
			'c0-id'		=> '0',
			'c0-param0'	=> '/showFlightLoadPopup.do?temp=temp&listId=' . $flightIndex . '&source=out&activeMenuForStandbyList=nonRevenue&search=search',
			'batchId'	=> '1',					   //^ This is the the source id for show pop ups				
			'page' 		=> 'nonRevenueSearch.do?search=getflights&travelWarningPresent=null',
			'httpSessionId' => 'EE50F5141B56A72B0AB5FA7FEC07EEA6',
			'scriptSessionId' => '351C5FB62D3F0FBE54BE95DC0C3BC264'
		
		);

		$showPopUpsRequest->addPostParameter($payloadRequest);
		$popUpsResponse = $showPopUpsRequest->send(); 

		file_put_contents($allFlightInformation, $popUpsResponse->getBody(), FILE_APPEND);

	
  	}



$pythonCall = 'python allFlightsParser.py ';
$args = $allFlightInformation . ' ' . $mainFlightPage . ' ' . $priorityCode . ' ' . $priorityDate . ' ' . '"' . $selectedDate . ' ' . $selectedTime . '"';

#$mystring = system($pythonCall . $args);		#Calling Python from PHP!

$f = popen($pythonCall . $args, 'r');
#
#

$debugfile = 'debug.txt';
file_put_contents($debugfile, $pythonCall . $args);

$pythonSMS = 'python send_sms.py ';

echo '<h1> After a rigorous computation, we have determined your best flight route! <br><br>';

if ($f) {
    while (($buffer = fgets($f, 4096)) !== false) {

	$bestTripInfo = explode(',', $buffer);
	$flightHeader = $bestTripInfo[0];
	$flightProb = 100.0 * (float)$bestTripInfo[1];
	$firstclassProb = 100.0 * (float)$bestTripInfo[2];
	$departTime = str_replace(' ', '', $bestTripInfo[3]);
	$arriveTime = str_replace(' ', '', $bestTripInfo[4]);

	echo '<h2>' . $flightHeader . '</h1>';
	echo '<h2>Departure: ' . $departTime . '</h2>';
	echo '<h2>Arrival: ' . $arriveTime . '</h2>';
	echo '<h2>Your chances of making this flight: ' . number_format($flightProb, 2) . ' percent</h2>';
	echo '<h2>Your chances of making first class: ' . number_format($firstclassProb, 2) . ' percent</h2>';
	echo '<br><br>';

	#$phoneToText = '9256429984';
	$phoneToText = str_replace('-', '', $phoneToText);
	$textFlightInfo = popen($pythonSMS . '"'. $flightHeader . ". This flight departs at " . $departTime . " and arrives at " . $arriveTime . ". Your chances of making this flight are " . number_format($flightProb, 2) . "% and of first class " . number_format($firstclassProb, 2) . "%. Safe travels!" . '"' . ' ' . $phoneToText, 'r');
	#$textFlightInfo = popen($pythonSMS . '"' . $flightHeader . '"', 'r');
	#$textFlightInfo = popen($pythonSMS . "Sent from dlnet server", 'r');
    }
    if (!feof($f)) {
        echo "Error: unexpected fgets() fail\n";
    }

    fclose($f);
}



echo 'Success';
#echo 'Best flighttrip: '. print_r($bestFlightTrip) . '<br>';

?>


