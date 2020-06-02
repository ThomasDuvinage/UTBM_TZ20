<?php



function db_connect() {

        // Define connection as a static variable, to avoid connecting more than once 
	static $bdd;

        // Try and connect to the database, if a connection has not been established yet
	if(!isset($bdd)) {
             // Load configuration as an array. Use the actual location of your configuration file
		$config = parse_ini_file('private/config.ini'); 
		try{
			$bdd = new PDO('mysql:host='.$config['servername'].';dbname='.$config['dbname'].';charset=utf8',$config['username'],$config['password'], 
				array(PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION));
		}
		catch(Exception $e){
			die('Erreur de connexion BDD : '.$e->getMessage());
		}
	}
	return $bdd;
}

// Connect to the database
$bdd = db_connect();

	$UID = $_GET['uid'];
	$req=$bdd->prepare('SELECT login FROM students WHERE UID = ?');
	$req->execute(array($UID));
	$res = $req->fetch();
	if(!empty($res)){
		$login = array('login',$res['login']);
		$porteur=array('porteur',$login);
		echo json_encode($porteur);
	}

?>