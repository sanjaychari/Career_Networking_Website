<?php

$con = mysqli_connect('localhost','root','','jobs');
if (!$con) {
    die('Could not connect: ' . mysqli_error($con));
}

$sql = "SELECT company_id FROM company WHERE company_name = '".$_GET['company']."'";
$result = mysqli_query($con,$sql);
if(!$result) {
  echo "Could not execute".mysqli_error($result);
}
$company_id = mysqli_fetch_array($result)['company_id'];

$sql = "SELECT user_id FROM user WHERE name = '".$_COOKIE['username']."'";
$result = mysqli_query($con,$sql);
if(!$result) {
  echo "Could not execute".mysqli_error($result);
}
$user_id = mysqli_fetch_array($result)['user_id'];

$sql = "INSERT INTO job VALUES('".$_GET['city']."','".$_GET['country']."','".$_GET['specs']."','".$_GET['term']."','".$_COOKIE['username']."','".$_GET['company']."','".$_GET['lowsal']."','".$_GET['highsal']."','".$user_id."','".$company_id."',DEFAULT)";
$result = mysqli_query($con,$sql);
if(!$result) {
  echo "Could not execute".mysqli_error($result);
}

echo "Job Created Successfully";
?>