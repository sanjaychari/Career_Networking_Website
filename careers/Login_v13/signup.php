<?php

if($_GET['password']!=$_GET['repeat_pass'])
{
  //echo "Password and repeat password do not match";
  exit('Password and repeat password do not match');
}
$con = mysqli_connect('localhost','root','','jobs');
if (!$con) {
    die('Could not connect: ' . mysqli_error($con));
}

/*if($location!="Anywhere")
{
    $sql="SELECT * FROM job WHERE city = '".$location."' AND term = '".$term."' AND specs LIKE '%".$specs."%'";
}
else
{
    $sql="SELECT * FROM job WHERE term = '".$term."' AND specs LIKE '%".$specs."%'";
}*/
$sql = "SELECT company_id FROM company WHERE company_name = '".$_GET['company_name']."'";
$result = mysqli_query($con,$sql);
if(!$result) {
  echo "Could not execute".mysqli_error($result);
}

if(mysqli_num_rows($result)==0)
{
  $sql = "INSERT INTO company VALUES(DEFAULT,'".$_GET['company_name']."','".$_GET['company_headquarters']."','".$_GET['category']."','".$_GET['ceo']."')";
  $result = mysqli_query($con,$sql);
  if(!$result) {
    echo "Could not execute".mysqli_error($result);
  }

  $sql = "SELECT company_id FROM company WHERE company_name = '".$_GET['company_name']."'";
  $result = mysqli_query($con,$sql);
  if(!$result) {
    echo "Could not execute".mysqli_error($result);
  }
}

$company_id = mysqli_fetch_array($result)['company_id'];

$sql = "INSERT INTO user VALUES('".$_GET['name']."','".$_GET['email']."','".$_GET['password']."',DEFAULT,'".$_GET['company_name']."','".$company_id."')";
$result = mysqli_query($con,$sql);
if(!$result) {
  echo "Could not execute".mysqli_error($result);
}

/*echo "<div class=\"row mb-5 justify-content-center\">
          <div class=\"col-md-7 text-center\">
            <h2 class=\"section-title mb-2\">".mysqli_num_rows($result)." Jobs Listed</h2>
          </div>
        </div>";

while($row = mysqli_fetch_array($result)) {
    echo "<div class=\"row align-items-start job-item border-bottom pb-3 mb-3 pt-3\">
            <div class=\"col-md-2\">
              <a href=\"job-single.html\"><img src=\"images/featured-listing-1.jpg\" alt=\"Image\" class=\"img-fluid\"></a>
            </div>
            <div class=\"col-md-4\">
              <span class=\"badge badge-primary px-2 py-1 mb-3\">".$term."</span>
              <h2><a href=\"job-single.html\">".$row['specs']."</a> </h2>
              <p class=\"meta\">Publisher: <strong>".$row['publisher']."</strong> In: <strong>".$row['company']."</strong></p>
            </div>
            <div class=\"col-md-3 text-left\">
              <h3>".$row['city']."</h3>
              <span class=\"meta\">".$row['country']."</span>
            </div>
            <div class=\"col-md-3 text-md-right\">
              <strong class=\"text-black\">".$row['lowsal']." &mdash; ".$row['highsal']."</strong>
            </div>
          </div>";
}
mysqli_close($con);
?>*/
setcookie("username", $_GET['name'], time() + (86400 * 30), "/");
echo "Profile Created Successfully";
?>