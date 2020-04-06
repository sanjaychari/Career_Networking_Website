<?php

if(!isset($_COOKIE['prev_num_rows']))
{
  setcookie("prev_num_rows", 0, time() + (86400 * 30), "/");
  $prev_num_rows = 0;
}
else
{
  $prev_num_rows = $_COOKIE['prev_num_rows'];
}

$con = mysqli_connect('localhost','root','','jobs');
if (!$con) {
    die('Could not connect: ' . mysqli_error($con));
}

if(isset($_GET['is_reload_needed']))
{
  $sql = "SELECT * FROM messages";
  $result = mysqli_query($con,$sql);
  if(!$result) {
    echo "Could not execute".mysqli_error($result);
  }
  $curr_num_rows = mysqli_num_rows($result);
  if($curr_num_rows!=$prev_num_rows)
  {
    setcookie("prev_num_rows", $curr_num_rows, time() + (86400 * 30), "/");
    echo "New Messages Added";
  }
  else
  {
    echo "No new message added";
  }
}

if(isset($_GET['search_tag']))
{
  $is_first = "1";
  $sql = "select user1_name,content,Date_Time,max(message_id) from ((select f.user1_name, f.content, f.Date_Time,f.message_id from (SELECT user1_name, MAX(message_id) as mess_id FROM messages WHERE user2_name = '".$_COOKIE['username']."' and (user1_name LIKE '%".$_GET['search_tag']."%' or content LIKE '%".$_GET['search_tag']."%') GROUP BY user1_name) as x inner join messages as f on f.user1_name = x.user1_name and f.message_id = x.mess_id and f.user1_name <> '".$_COOKIE['username']."') UNION (select f.user2_name, f.content, f.Date_Time,f.message_id from (SELECT user2_name, MAX(message_id) as mess_id FROM messages WHERE user1_name = '".$_COOKIE['username']."' and (user2_name LIKE '%".$_GET['search_tag']."%' or content LIKE '%".$_GET['search_tag']."%') GROUP BY user2_name) as x inner join messages as f on f.user2_name = x.user2_name and f.message_id = x.mess_id and f.user2_name <> '".$_COOKIE['username']."') ORDER BY Date_Time DESC) as temp group by user1_name order by Date_Time";
  $result = mysqli_query($con,$sql);
  if(!$result) {
    echo "Could not execute".mysqli_error($result);
  }

  /*$sql = "select f.user2_name, f.content, f.Date_Time
from (SELECT user2_name, MAX(message_id) as mess_id FROM messages WHERE user2_name LIKE '%".$_GET['search_tag']."%' OR (content LIKE '%".$_GET['search_tag']."%'  AND user1_name = '".$_COOKIE['username']."') GROUP BY user2_name) as x inner join messages as f on f.user2_name = x.user2_name and f.message_id = x.mess_id and f.user2_name <> '".$_COOKIE['username']."'  ORDER BY f.message_id DESC;";
  $result2 = mysqli_query($con,$sql);
  if(!$result2) {
    echo "Could not execute".mysqli_error($result1);
  }*/

  if(mysqli_num_rows($result)==0)
  {
    echo "No Data to be Displayed";
  }

  while($row = mysqli_fetch_array($result)) {
      echo "<div class=\"chat_list\" id=\"".$row['user1_name']."\" onclick=\"change_active('".$row['user1_name']."');\">
              <div class=\"chat_people\">
                <div class=\"chat_img\"> <img src=\"https://ptetutorials.com/images/user-profile.png\" alt=\"".$row['user1_name']."\"> </div>
                <div class=\"chat_ib\">
                  <h5>".$row['user1_name']." <span class=\"chat_date\">".$row['Date_Time']."</span></h5>
                  <p>".$row['content']."</p>
                </div>
              </div>
            </div>";
  }

  /*while($row = mysqli_fetch_array($result2)) {
    echo "<div class=\"chat_list\" id=\"".$row['user2_name']."\" onclick=\"change_active('".$row['user2_name']."');\">
              <div class=\"chat_people\">
                <div class=\"chat_img\"> <img src=\"https://ptetutorials.com/images/user-profile.png\" alt=\"".$row['user2_name']."\"> </div>
                <div class=\"chat_ib\">
                  <h5>".$row['user2_name']." <span class=\"chat_date\">".$row['Date_Time']."</span></h5>
                  <p>".$row['content']."</p>
                </div>
              </div>
            </div>";
  }*/

}

if(isset($_GET['fetchdata']))
{
  if(isset($_GET['active_user']))
  {
    $active=$_GET['active_user'];
  }
  $sql = "select user1_name,content,Date_Time,max(message_id) from ((select f.user1_name, f.content, f.Date_Time,f.message_id from (SELECT user1_name, MAX(message_id) as mess_id FROM messages WHERE user2_name = '".$_COOKIE['username']."' GROUP BY user1_name) as x inner join messages as f on f.user1_name = x.user1_name and f.message_id = x.mess_id and f.user1_name <> '".$_COOKIE['username']."') UNION (select f.user2_name, f.content, f.Date_Time,f.message_id from (SELECT user2_name, MAX(message_id) as mess_id FROM messages WHERE user1_name = '".$_COOKIE['username']."' GROUP BY user2_name) as x inner join messages as f on f.user2_name = x.user2_name and f.message_id = x.mess_id and f.user2_name <> '".$_COOKIE['username']."') ORDER BY Date_Time DESC) as temp group by user1_name order by Date_Time";
  $result = mysqli_query($con,$sql);
  if(!$result) {
    echo "Could not execute".mysqli_error($result);
  }

  /*$sql = "select f.user2_name, f.content, f.Date_Time
from (SELECT user2_name, MAX(message_id) as mess_id FROM messages WHERE user1_name = '".$_COOKIE['username']."' GROUP BY user2_name) as x inner join messages as f on f.user2_name = x.user2_name and f.message_id = x.mess_id and f.user2_name <> '".$_COOKIE['username']."' ORDER BY f.message_id DESC;";
  $result2 = mysqli_query($con,$sql);
  if(!$result2) {
    echo "Could not execute".mysqli_error($result1);
  }*/

  if(mysqli_num_rows($result)==0)
  {
    echo "No Data to be Displayed";
  }

  while($row = mysqli_fetch_array($result)) {
    if(isset($_GET['active_user']) and $row['user1_name']==$_GET['active_user'])
    {
      echo "<div class=\"chat_list active_chat\" id=\"".$row['user1_name']."\" onclick=\"change_active('".$row['user1_name']."');\">
              <div class=\"chat_people\" >
                <div class=\"chat_img\"> <img src=\"https://ptetutorials.com/images/user-profile.png\" alt=\"".$row['user1_name']."\"> </div>
                <div class=\"chat_ib\">
                  <h5>".$row['user1_name']." <span class=\"chat_date\">".$row['Date_Time']."</span></h5>
                  <p>".$row['content']."</p>
                </div>
              </div>
            </div>";
    }
    else
    {
      echo "<div class=\"chat_list\" id=\"".$row['user1_name']."\" onclick=\"change_active('".$row['user1_name']."');\">
              <div class=\"chat_people\" >
                <div class=\"chat_img\"> <img src=\"https://ptetutorials.com/images/user-profile.png\" alt=\"".$row['user1_name']."\"> </div>
                <div class=\"chat_ib\">
                  <h5>".$row['user1_name']." <span class=\"chat_date\">".$row['Date_Time']."</span></h5>
                  <p>".$row['content']."</p>
                </div>
              </div>
            </div>";
    }
  }

  /*while($row = mysqli_fetch_array($result2)) {
    if(isset($_GET['active_user']) and $row['user2_name']==$_GET['active_user'])
    {
      echo "<div class=\"chat_list active_chat\" id=\"".$row['user2_name']."\" onclick=\"change_active('".$row['user2_name']."');\">
              <div class=\"chat_people\" >
                <div class=\"chat_img\"> <img src=\"https://ptetutorials.com/images/user-profile.png\" alt=\"".$row['user2_name']."\"> </div>
                <div class=\"chat_ib\">
                  <h5>".$row['user2_name']." <span class=\"chat_date\">".$row['Date_Time']."</span></h5>
                  <p>".$row['content']."</p>
                </div>
              </div>
            </div>";
    }
    else
    {
    echo "<div class=\"chat_list\" id=\"".$row['user2_name']."\" onclick=\"change_active('".$row['user2_name']."');\">
              <div class=\"chat_people\">
                <div class=\"chat_img\"> <img src=\"https://ptetutorials.com/images/user-profile.png\" alt=\"".$row['user2_name']."\"> </div>
                <div class=\"chat_ib\">
                  <h5>".$row['user2_name']." <span class=\"chat_date\">".$row['Date_Time']."</span></h5>
                  <p>".$row['content']."</p>
                </div>
              </div>
            </div>";
    }
  }*/
}

if(isset($_GET['display_messages']))
{
  $sql = "SELECT content,Date_Time,user1_name,user2_name FROM messages WHERE (user1_name = '".$_GET['active_user']."' and user2_name = '".$_COOKIE['username']."') OR (user2_name = '".$_GET['active_user']."' and user1_name = '".$_COOKIE['username']."') ORDER BY Date_Time";
  $result = mysqli_query($con,$sql);
  if(!$result) {
    echo "Could not execute".mysqli_error($result);
  }
  while($row = mysqli_fetch_array($result)) {
    if($row['user1_name']==$_GET['active_user'])
    {
    echo "<div class=\"incoming_msg\">
              <div class=\"incoming_msg_img\"> <img src=\"https://ptetutorials.com/images/user-profile.png\" alt=\"".$row['user1_name']."\"> </div>
              <div class=\"received_msg\">
                <div class=\"received_withd_msg\">
                  <p>".$row['content']."</p>
                  <span class=\"time_date\">".$row['Date_Time']."</span></div>
              </div>
            </div>";
    }
    else
    {
      echo "<div class=\"outgoing_msg\">
              <div class=\"sent_msg\">
                <p>".$row['content']."</p>
                <span class=\"time_date\">".$row['Date_Time']."</span> </div>
            </div>";
    }
  }
  echo "<div class=\"type_msg\">
            <div class=\"input_msg_write\">
              <input type=\"text\" class=\"write_msg\" placeholder=\"Type a message\" id=\"message_to_send\">
              <button class=\"msg_send_btn\" type=\"button\" onclick=\"send_message();\"><i class=\"fa fa-paper-plane-o\" aria-hidden=\"true\"></i></button>
            </div>";
}

if(isset($_GET['send_message']))
{
  $sql = "SELECT user_id FROM user WHERE name = '".$_COOKIE['username']."'";
  $result = mysqli_query($con,$sql);
  if(!$result) {
    echo "Could not execute".mysqli_error($result);
  }
  $row = mysqli_fetch_array($result);
  $user1_id = $row['user_id'];

  $sql = "SELECT user_id FROM user WHERE name = '".$_GET['active_user']."'";
  $result = mysqli_query($con,$sql);
  if(!$result) {
    echo "Could not execute".mysqli_error($result);
  }
  $row = mysqli_fetch_array($result);
  $user2_id = $row['user_id'];

  $sql = "INSERT INTO messages VALUES('".$user1_id."','".$user2_id."','".$_COOKIE['username']."','".$_GET['active_user']."','".$_GET['send_message']."',NOW(),DEFAULT)";
  $result = mysqli_query($con,$sql);
  if(!$result) {
    echo "Could not execute".mysqli_error($result);
  }
  //$row = mysqli_fetch_array($result);
  echo "Message Sent Successfully";
}

mysqli_close($con);
?>