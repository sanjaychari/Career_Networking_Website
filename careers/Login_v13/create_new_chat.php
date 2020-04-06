<?php
$con = mysqli_connect('localhost','root','','jobs');
if (!$con) {
    die('Could not connect: ' . mysqli_error($con));
}

$sql = "SELECT user_id FROM user WHERE name = '".$_COOKIE['username']."'";
$result = mysqli_query($con,$sql);
if(!$result) {
	echo "Could not execute".mysqli_error($result);
}
$row = mysqli_fetch_array($result);
$user1_id = $row['user_id'];

$sql = "SELECT user_id FROM user WHERE name = '".$_GET['name']."'";
$result = mysqli_query($con,$sql);
if(!$result) {
    echo "Could not execute".mysqli_error($result);
}
$row = mysqli_fetch_array($result);
$user2_id = $row['user_id'];

$sql = "INSERT INTO messages VALUES('".$user1_id."','".$user2_id."','".$_COOKIE['username']."','".$_GET['name']."','".$_GET['content']."',NOW(),DEFAULT)";
$result = mysqli_query($con,$sql);
if(!$result) {
    echo "Could not execute".mysqli_error($result);
}
  //$row = mysqli_fetch_array($result);
echo "Message Sent Successfully";
?>