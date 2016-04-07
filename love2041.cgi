#!/usr/bin/perl -w

use CGI qw/:all/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Data::Dumper;  
use File::Copy;
use List::Util qw/min max/;
warningsToBrowser(1);

# print start of HTML ASAP to assist debugging if there is an error in the script
print page_header();

# some globals used through the script
$debug = 1; # sets whether to display debug details
$students_dir = "./students"; #students directory, (was given in starting code..)
$suspended_students_dir = "./suspended_students"; # just a new variable to contain directory with suspended student's files.
$unactivated_students_dir = "./unactivated_students"; # contain directory with the unactivated_student's files.
$username = param('studentName') if (defined param ('studentName')); # who we are currently logged in as
@studentNames = glob("$students_dir/*"); # array containing all of the student names
foreach my $student (@studentNames) { #remove the directory path from name
   $student =~ s/$students_dir\///;
}

%stuDetails; # format: $stuDetails{'Category'}{'Answer'}
# where this element in the hash of hashes is an array that contains all usernames that fit this preference

%matchScore; # format: $matchScore{'Username'}
# hash which contains the match Score

main();
print page_trailer();
exit 0;	

# Function: main
# Main function says which function to call for certain states
# 
sub main {
   if (! defined param() || param ("Logout")) {       # if logout button is pressed, or just accessed site, display login page
      display_login_form();
      exit;
   } elsif (defined param("username") && defined param("password") && param("Login")) {   # check if username and password are correct
      param ('studentName', param("username"));
      login_checker();
   } elsif (param("Create account")) {                # create account button is pressed, display form
      display_create_account_form();
   } elsif (param("createEmail") && param("createPass") && param("createUser")) {         # completed account creation form, send email
      send_verification_mail();
   } elsif (param("Forgot password")) {               # forgot password button was pressed, display form
      print display_forgot_password_form();
   } elsif (param("activate")) {                      # verificationLink was clicked on email, create account.
      create_account();
   } elsif (defined param("forgotPass")) {            # completed Forgot password form, send email
      send_mail_to_change_password();
   } elsif (param("passChange")) {                    # Link was clicked on email to change password, display form for new password
      display_new_password_form();
      if (param("newPassword") && param("confirmPassword") && param("confirmPassword")) {             # If form was filled out
         change_password(param("newPassword"), param("passChange"), param("confirmPassword"));
      } elsif (param("newPassword") eq "" || param("confirmPassword") eq "" || param("confirmPassword") eq "") { # Double check if actually filled out
         print p("Error: Please fill in all the fields above.");
      }
   } elsif (param('Reactivate account')) {            # Activate current account (should only be if currently suspended)
      activate_account();
   } elsif (param("studentName")) {                   # we are logged in, print the toolbar
      print toolbar();
   }
   
   #### SHOULD ONLY BE ABLE TO ACCESS THESE PAGES BELOW IF LOGGED IN ####
   
   if (param("Next student")) {                                   # Go to next student on display_profile_screen
      print display_profile_screen(1);
   } elsif (param("Next set")) {                                  # Go to next set of profiles
      print display_sets(10);
   } elsif (param("View users")) {                                # Go to the display_sets screen
      print display_sets(0);
   } elsif (param("Previous student")) {                          # Go to previous student on display_profile_screen
      print display_profile_screen(-1);
   } elsif (param("Previous set")) {                              # Go to previous set of profiles
      print display_sets(-10);
   } elsif (param("user")) {                                      # Go to specific user profile page
      print display_profile_screen("specific", param("user"));
   } elsif (param("Next page") && param ("Searchfield")) {        # Go to next page on search state
      print display_search(10);
   } elsif (param("Prev page") && param ("Searchfield")) {        # Go to previous page on search state
      print display_search(-10);
   } elsif (param("Find best matches") && param("studentName")) { # Go to page to display best matches
      print display_best_matches(0);;
   } elsif (param("Random student")) {                            # Display a random student's profile
      print display_profile_screen("random");
   } elsif (param("Previous best set")) {                         # Go to the previous set on best matches page
      print display_best_matches(-10);
   } elsif (param("Next best set")) {                             # Go to the next set on the best matches page 
      print display_best_matches(10);
   } elsif (param("View your profile")) {                         # View your own profile
      print display_profile_screen("specific", param("studentName"));
   } elsif (param("View user settings")) {                        # Display user settings, and operate depending on other params passed in
                              ### States to enter in user settings ###
      print settings_toolbar();
      if (param('Edit profile description')) {                    # Edit additional text added by user
         display_profile_description_form();
      } elsif (param('Suspend account')) {                        # Suspend current account (should only be if not suspended currently)
         display_suspend_account_form();
         if (param("currentPassword")) {                          # After password has been typed, run suspend_account() - handles password checking
            suspend_account();
         }
      } elsif (param('Delete account')) {                         # Delete user account from students directory
         display_delete_account_form();
         if (param("currentPassword")) {                          # After password has been typed, run delete_account() - handles password checking
            delete_account();
         }
      } elsif (param('Change password')) {                        # Display form to change password
         display_change_password_form();
         if (defined param("newPassword") && defined param("studentName") && 
             defined param("currentPassword") && defined param("confirmPassword")) {  # if all necessary parameters are defined
            change_password(param("newPassword"), encrypt(param("studentName")), param("confirmPassword"), param("currentPassword")); # change password
         }
      } elsif (param('Edit preferences')) {                       # Display edit preferences form
         display_edit_preferences_form();
      } elsif (param('Edit profile details')) {                   # Display edit profile page form
         print "To be completed\n";
      } elsif (param('Upload image')) {                           # Display upload image form
         display_upload_image_form();
         if (defined param('filename')) {                         # Image uploading form has been filled.
            upload_image();
         }
      } elsif (param('Delete image')) {                           # Display delete_image form
         display_delete_image_form();
      } elsif (param('Change profile image')) {                   # Display change profile form
         display_change_profile_image_form();
      } elsif (param('Change info')) {                            # Filled in additional information, change it now
         change_profile_description();
      } elsif (param('imageToDelete') && param('imageDel')) {     # Once delete_image_confirmation form is filled out
         if (param('imageDel') eq "Confirm") {                    # Check if Confirmed then delete
            delete_image(param('imageToDelete'));
         } else {                                                 # Otherwise display delete form again
            display_delete_image_form();
         }
      } elsif (param('imageToDelete')) {                          # Display confirmation page.
         display_delete_image_confirmation_form();
      } elsif (param('swapProfileImage')) {                       # If chosen image to swap to become profile image
         change_profile_image(param('swapProfileImage'));
      } elsif (param('Change preferences')) {
         change_preferences();
      } else {
         print h1("Welcome to user settings!", p, 
         "Click on one of the buttons in the toolbar above to change your account details\n");
      }
   } elsif (param('Message')) {                                   # If message button clicked on while browsing profiles
      display_messaging_form();
   } elsif (param('Send message')) {                              # Finished filling messaging form, send message now
      send_message();
   } elsif (param("Searchfield")) {                               # Initiate searching 
      print display_search(0);
   } elsif (param("aboutMatching")) {
      display_matching_algo();
   }
}

   ############################################################
   # Functions to help website navigation and display website #
   ############################################################

# Function: page_header 
# HTML placed at the top of every screen
#
sub page_header {
	return header,
   		start_html("-title"=>"LOVE2041", -bgcolor=>"#000000", -style=>{'src'=>'love2041.css'}),
         center(h1(i("LOVE2041<p>")));
}

# Function: toolbar
# HTML placed at the top of every page for easy navigation of website
# Should only be available after login
# Also passes in the student's username that is currently logged in
#
sub toolbar {
   my $username = param('studentName');
   return h1("Welcome $username!"),
         start_form,
         textfield('Searchfield', "Type here to search for user"), "\n", 
         submit('Searchfield', 'Search'), "\n",
         submit('View users'), "\n",
         hidden('studentName'), "\n",
         submit('View your profile'), "\n",
         submit('Find best matches'), "\n",
         submit('View user settings'), "\n",
         submit('Logout'),
         end_form, p, hr;
}

# Function: settings_toolbar
# Prints out a toolbar of possible things to do with their account
#
sub settings_toolbar {
   return start_form,
         submit('Edit profile description'), "\n",
         submit('Suspend account'), "\n",
         submit('Delete account'), "\n",
         submit('Change password'), "\n",
         submit('Upload image'), "\n",
         submit('Delete image'), "\n",
         submit('Change profile image'), "\n",
         submit('Edit preferences'), "\n",
         submit('Edit profile details'), "\n",
         hidden('studentName'), "\n",
         hidden('View user settings'),
         end_form;
}
# Function: page_trailer
# HTML placed at bottom of every screen
# It includes all supplied parameter values as a HTML comment
# if global variable $debug is set
#
sub page_trailer {
	my $html = "";
	$html .= join("", map("<!-- $_=".param($_)." -->\n", param())) if $debug; 
	$html .= end_html;
	return $html;
}

   ##############################################################
   # Functions that display profiles and/or profile information #
   ##############################################################

# Function: display_profile_screen
# This function displays the profile page with user details
# Input 1: Change in students (dependent on whether next/prev student button is pressed, or view users button pressed)
#          Can only be -1, 0 or 1 (Prev student = -1, View users = 0, Next student = 1)
# Input 2: Optional, only when we want to display a certain user, e.g. username was clicked on when viewing profile sets
#          Has the username in this scalar string
#
sub display_profile_screen ($$) {
   my @students = glob("$students_dir/*");
   my $n = param('n') || 0;  # initialize $n
   if ($_[0] eq "specific") { # display specific student
      my $userToSearch = $_[1];
      $userToSearch =~ s/^\d*\. //; # remove the Rank 
      $userToSearch =~ s/ \(score: \d*\)$//; # remove the Score
      $n = userToIndex($userToSearch, 0);
      if ($n == -1) {         # findUser will return -1 if invalid username is specified
         print "User '$userToSearch' not found. Please try again.";
         return;              # exit function, so it won't print anything else.
      }
   } elsif ($_[0] eq "random") {
      $n = int(rand(@students));
   } else {
      my $alteration = $_[0];
      $n = $n + $alteration;  #increment or decrement n depending on value of $alteration
      $n = 0 if ($alteration == 0); # if we display from first student, we set $n to 0
   }
   $n = 0 if ($n < 0);                   # if at first student, prev student button won't make it go to last student
   $n = $#students if ($n >= @students); # Next student after last one is still last.
   
   print p, start_form;
   print submit('Previous student'), "\n" if ($n > 0);  # only display previous student button when it goes to different page
   print submit('Random student'), "\n";
   print submit('Next student') if ($n < $#students);   # only display next student button when it goes to a different page
   print p, submit('Message');
	my $student_to_show  = $students[$n];
	my $profile_filename = "$student_to_show/profile.txt";
   my @details = information_filter ($profile_filename); # remove real name, courses taken, password, etc from profile page
	$profile = join '', @details; # put all of it into a scalar string to be printed
   param('n', $n);
   print "<img src='$student_to_show/profile.jpg' align='right'>" if (-e "$student_to_show/profile.jpg"); # prints profile image on right if it exists
   print "<img src='default_profile.jpg' align='right'>" if (-e "$student_to_show/profile.jpg" == 0); # prints default profile image if one doesn't exist.
   print pre($profile);                                            # prints out all profile details as displayed in file
   display_other_pictures($student_to_show);
  	return hidden ('n'),
      hidden ('studentName'),
		end_form, "\n",
		p;
}

# Function: display_other_pictures
# Function which prints out the other photos of the student
# Should only appear on the bottom of the display_profile_screen page
# Input 1: scalar variable containing path to student username directory
#
sub display_other_pictures ($) {
   my $studentDirectory = $_[0];
   my @profileImages = glob ("$studentDirectory/photo*");
   foreach my $image (@profileImages) {
      print "\n<img src='$image'>\n";
   }
}

# Function: display_sets
# Displays a set of 10 students on page with clickable submit buttons to 
# View more of their details
# Input 1: Says whether to go back or restart display to first page.
#
sub display_sets ($) {
   my @students = glob("$students_dir/*");
   my $alteration = $_[0];
   my $s = param ("s"); # index in the array
   if ($alteration < 0) {
      $s = $s + 2 * $alteration; # if it is negative then go back twice the value (going back once would just print the current set displayed)
      $s = $s + (10 - ($s % 10)) if ($s !~ /0$/);  # if it is at end then it needs to go back a certain number.
   } elsif ($alteration == 0) { # if it just starts, then set $s to 0
      $s = 0;
   }
   $s = 0 if ($s < 0 || $alteration == 0);                    # if we are at first student, prev set button just displays first student set.
   
   print start_form;
   print submit ('Previous set', 'Previous page'), "\n" if ($s > 0);   # should only display previous set button when it does anything
   print submit ('Next set', 'Next page') if ($s + 10 <= $#students);  # should only display next set button if page actually changes
   print p;                                                            # print next and previous set buttons
   
   my @studentUsernames = ();
   foreach (1..2) {                                      # loop for two rows
      foreach (1..5) {                                   # loop for 5 students per row
         last if ($s >= @studentNames);                  # stop printing after last student
	      my $student_to_show  = $students[$s];
         $s++;
         print "<img src='$student_to_show/profile.jpg' align='center'>\n" if (-e "$student_to_show/profile.jpg"); # prints profile image
         print "<img src='default_profile.jpg' align='center'>\n" if (-e "$student_to_show/profile.jpg" == 0); # prints default if it doesn't exist
         $student_to_show =~ s/\.\/students\///;
         push (@studentUsernames, $student_to_show);     # fill array with the student names to put in the submit button below
      }
      
      print p;
      foreach my $studentUsername(@studentUsernames) {   # after printing profile image it prints the username submit button underneath
         print "<input type='submit' name='user' value='$studentUsername' style='height:30px; width:250px' />\n";
      }
      print p;
      @studentUsernames = ();
   }
   param ('s', $s);                   # set param 's' with value $s
   return hidden ('s'), 
          hidden ('studentName'),
          end_form;                   # then return it
}

# Function: display_best_matches
# Prints out the best matches for the user as sets of ten
# Input 1: Contains the current 'depth' in the sets, used to determine which set to print
#
sub display_best_matches ($) {
   find_match();
   my $alteration = $_[0];
   my @matches = sort {$matchScore{$b} <=> $matchScore{$a}} keys %matchScore; # sort numerically for matchScores
   if (@matches == 1) {
      print h1("Sorry no matches found!", p, "Please provide more profile details or more preferences");
      return;
   }
   my $rank = param ('b') || 1;
   if ($alteration == 0) { #display first page
      $rank = 1;
   } elsif ($alteration == -10) {
      $rank = $rank + 2 * $alteration; # go back one set, twice because once only prints current set
      $rank = $rank - (9 + ($rank % 10)) if ($rank !~ /1$/); # if it is at end then it needs to go back a certain number.
      $rank = 1 if ($rank <= 0); # set negative values to be first set
   }
   
   my $lastIndexToPrint;
   foreach $count (0..$#matches) { # loop which calculates max index to stop printing at
      if ($matchScore{$matches[$count]} <= 0) { # it will stop printing when the matchScore is less than or equal to zero
         $lastIndexToPrint = $count;
         last;
      }
   }
   $rank = $lastIndexToPrint - ($lastIndexToPrint % 10) + 1 if ($rank > $lastIndexToPrint); # set it to display last set if it tries to overflow
   
   print start_form;
   print submit ('Previous best set', 'Previous page'), "\n" if ($rank > 1);
   print submit ('Next best set', 'Next page') if ($rank + 10 <= $lastIndexToPrint);
   print p;
   
   my @users = ();
   foreach my $userName ($rank..$rank+9) { #goes through each of them
      last if ($userName >= $lastIndexToPrint); # Stop printing when it reaches lastIndexToPrint
      print "<img src='$students_dir/$matches[$userName-1]/profile.jpg' align='center'>\n" if (-e "$students_dir/$matches[$userName-1]/profile.jpg");
      print "<img src ='default_profile.jpg' align='center'>\n" if (-e "$students_dir/$matches[$userName-1]/profile.jpg" == 0);
      push (@users, "$userName. $matches[$userName-1] (score: $matchScore{$matches[$userName-1]})"); # pushes namesToPrint onto array
      if ($userName % 5 == 0) {
         print p;
         foreach my $user (@users) {
            print "<input type='submit' name='user' value='$user' style='height:30px; width:250px' />\n";
         }
         print p;
         @users = (); # reset the array for new list of usernames to print
      }  
   }
   if (@users != 0) { # if there is still stuff to print
      print p;
      foreach my $user (@users) {
         print "<input type='submit' name='user' value='$user' style='height:30px; width:250px' />\n";
      }
      print p;
   }
   param ('b', $rank + 10);
   return hidden ('studentName'), 
          hidden ('b'), end_form;
}

# Function: display_search
# Function which displays a set of usernames which match the searchTerm 
# If there exists a user with the matching searchTerm then go to their profile page
# SearchTerm must contain at least 3 characters
# Input 1: Scalar which tells us which set to display (if it's negative: go back one set, 0: display first set)
#
sub display_search ($) {
   my $index = param ('search') || 0; # initialize variable
   my $alteration = $_[0];
   if ($alteration < 0) {
      $index = $index + 2 * $alteration; # go back one set, twice because once only prints current set
      $index = $index - (9 + ($index % 10)) if ($index !~ /0$/); # if it is at end then it needs to go back a certain number.
   }
   $index = 0 if ($alteration == 0 || $index <= 0); # set index to 0 if it was negative or $alteration = 0 (display first set)
   if (length(param("Searchfield")) < 3) {
      print "Search string must be at least 3 characters long. Please search again.";
      return;
   }
   my @namesToDisplay = userSearch (param("Searchfield"));
   my $searchString = param("Searchfield");
   if (@namesToDisplay == 1 && $searchString =~ /$namesToDisplay[0]/i) { # if there is only one name and name is same as username except for case
      print display_profile_screen ("specific", $namesToDisplay[0]);
      return;
   }
   # Begin printing set of possible searches
   print "User '$searchString' not found. Please try again. "; # message for user
   print "Did you mean.." if (@namesToDisplay != 0) ; # if there are actually possible matches print this line
   print start_form; 
   print submit ('Prev page', 'Previous page'), "\n" if ($index != 0);
   print submit ('Next page') if ($index + 10 < $#namesToDisplay);
   print p;
   my $stuffToPrint = 0;
   foreach my $student ($index..$index+9) {
      if ($student > $#namesToDisplay) { # break once we reach end
         print p;
         $stuffToPrint = $student % 5 if ($student % 5 != 0); # check if there's still stuff that need to be printed
         last;
      }
      print "<img src='$students_dir/$namesToDisplay[$student]/profile.jpg' align='center'>\n" if (-e "$students_dir/$namesToDisplay[$student]/profile.jpg");
      print "<img src='default_profile.jpg' align='center'>\n" if (-e "$students_dir/$namesToDisplay[$student]/profile.jpg" == 0);
      if ($student % 5 == 4) { # print a new row
         print p;
         foreach (1..5) { #run 5 times, loop to print out 5 user name submit buttons
            my $user = $namesToDisplay[$student - 5 + $_];
            print "<input type='submit' name='user' value='$user' style='height:30px; width:250px' />\n";
         }
         print p;
      }  
   }
   while ($stuffToPrint > 0) { # if stuff still need to be printed, loop and print the rest
      my $user = $namesToDisplay[@namesToDisplay - $stuffToPrint];
      print "<input type='submit' name='user' value='$user' style='height:30px; width:250px' />\n";
      $stuffToPrint--;
   }
   param ('search', $index + 10);
   return hidden('studentName'), 
          hidden('search'), hidden ('Searchfield'),
          end_form;
}

   ################################
   # Display forms for user input #
   ################################

# Function: display_login_form
# Function which displays login page with the username and password field
#
sub display_login_form {
   print start_form,
         center(p, 'Username: ', textfield("username")),
         center(p, 'Password: ', password_field("password")),
         center(p, submit ('Login')),
         center(p, submit ('Create account'), 
         submit ('Forgot password')),
         end_form;
}

# Function: display_create_account_form
# Function which displays the form to create an account
#
sub display_create_account_form {
   print start_form,
         h2(p("Create a new account:")),
         p("Enter your desired username: ", textfield("createUser")),
         p("Enter your desired password: ", password_field("createPass")),
         p("Enter e-mail address: ", textfield("createEmail")),
         submit('Logout', 'Go back to login'), "\n",
         submit('submit', 'Create account'), "\n",
         end_form;
}

# Function: display_forgot_password_form
# Displays the form to enter the username of account with forgotten password
#
sub display_forgot_password_form {
   return start_form,
         h2(p("Forgot your password:")),
         p("Enter your username: ", textfield("forgotPass")),
         submit,
         end_form;
}

# Function: display_new_password_form
# Prints out the form for a new password,
# Called after link is clicked for forgotten password
# Also keeps the parameter 'passChange' - contains the username of the password we are changing
#
sub display_new_password_form {
   print start_form,
         p("Enter your new password: ", password_field ('newPassword')),
         p("Re-enter new password: ", password_field ('confirmPassword')),
         submit,
         hidden("passChange"),
         end_form;
}

# Function: display_change_password_form
# Prints out the change password form, which is different from forgot password
# As there is a box for old password
#
sub display_change_password_form {
   print start_form,
         h1("Change password:"),
         p("Enter your current password: ", password_field ('currentPassword')),
         p("Enter your new password: ", password_field ('newPassword')),
         p("Re-enter new password: ", password_field ('confirmPassword')),
         submit,
         hidden('studentName'),
         hidden('View user settings'),
         hidden('Change password'),
         end_form;
}

# Function: display_profile_description_form
# Function which lets the user edit their current profile description
#
sub display_profile_description_form {
   open my $fh, "<$students_dir/$username/profile.txt" or die "Unable to open '$students_dir/$username/profile.txt': $!";
   my @newProfileTxt = <$fh>;
   close $fh;
   
   my $additionalExists = 0;
   my $extraInfo = ""; # initialize variables
   foreach $lineNumber (0..$#newProfileTxt) { # go through each line in profile.txt
      $extraInfo .= $newProfileTxt if ($additionalExists); #add onto variable if it exists
      $additionalExists = 1 if ($newProfileTxt[$lineNumber] =~ /^Additional information:/); # if the line is Additional information, add everything on afterwards.
   }
   
   print p, start_form, "Additional information:", p,
         "<textarea cols='60' rows='15' name='Extra info'>$extraInfo</textarea>", p,
         submit('Change info'),
         hidden('studentName'),
         hidden('View user settings'),
         end_form; # print a textbox containing $extraInfo inside
}

# Function: display_messaging_form
# Displays the form for user to fill out subject and message to send to this person
#
sub display_messaging_form {
   my $to = param('n');
   $to = $studentNames[$to];
   print start_form,
         "To: $to", p,
         "Subject: ", "\n",
         textfield('subject'), p,
         "Message:", p,
         "<textarea cols='60' rows='15' name='message'></textarea>", p,
         submit('Send message'),
         hidden('studentName');
         
   param ('to', $to); # save this parameter
   print hidden('to'),
         end_form;
}

# Function: display_delete_account_form
# Display the delete_account form, user has to enter his current password to confirm deletion.
# 

sub display_delete_account_form {
   print start_form,
         h1("Confirmation page to delete account"),
         p("Enter your current password: ", password_field ('currentPassword')),
         submit,
         hidden('studentName'),
         hidden('View user settings'),
         hidden('Delete account'),
         end_form;
}

# Function: display_suspend_account_form
# Display the suspend_account form, user has to enter his current password to confirm deletion.
#
sub display_suspend_account_form {
   print start_form,
         h1("Confirmation page to suspend account"),
         p("Enter your current password: ", password_field ('currentPassword')),
         submit,
         hidden('studentName'),
         hidden('View user settings'),
         hidden('Suspend account'),
         end_form;
}

# Function: display_upload_image_form
# Display the upload_image_form, user has to click a button and choose the file he wants to upload.
# Then he clicks the "Upload image" button to continue.
#
sub display_upload_image_form {
   print p, start_form, 
         h1 ("Click button below to upload image"), p
         hidden('studentName'),
         hidden('View user settings'),
         filefield('filename'), p,
         submit('Upload image'), p,
         end_form;
}

# Function: display_delete_image_form
# Display the delete_image_form, user clicks on one of the submit buttons under the image they want to delete.
#
sub display_delete_image_form {
   my @photos = glob ("$students_dir/$username/photo*");
   if (@photos == 0 && -e "$students_dir/$username/profile.jpg" == 0) {
      print h1("No images available to delete.");
      return;
   }
   print h1("To delete an image: Click on the button underneath the image you want to delete");
   print p, start_form;
   my @photoNames = (); # array containing photo names
   foreach my $photoNumber (0..$#photos) {
      print "\n<img src='$photos[$photoNumber]'>\n";
      $photos[$photoNumber] =~ s/$students_dir\/$username\///; # remove the directory path
      push (@photoNames, $photos[$photoNumber]);
      if ($photoNumber % 5 == 4) {
         print p;
         foreach my $photoName (@photoNames) {
            print "<input type='submit' name='imageToDelete' value='$photoName' style='height:30px; width:250px' />\n";
         }
         print p;
         @photoNames = (); # reset the array for new list of photonames to print
      }  
   }
   print "\n<img src='$students_dir/$username/profile.jpg'>\n" if (-e "$students_dir/$username/profile.jpg"); # print profile.jpg to delete if it exists
   print p;
   while (@photoNames > 0) { # if we still have names to print, print the rest out.
      my $photoName = shift (@photoNames);
      print "<input type='submit' name='imageToDelete' value='$photoName' style='height:30px; width:250px' />\n";
   }
   print "<input type='submit' name='imageToDelete' value='profile.jpg' style='height:30px; width:250px' />\n" if (-e "$students_dir/$username/profile.jpg");
   
   
   print hidden('studentName'),
         hidden('View user settings'),
         end_form;
}

# Function: display_delete_image_confirmation_form
# Display confirmation form for user to delete the image
#
sub display_delete_image_confirmation_form {
   my $imageToDelete = param("imageToDelete");
   print start_form,
         h1 ("Please confirm you want to delete the image below"),
         "\n<img src='$students_dir/$username/$imageToDelete'>\n", p,
         submit('Delete image', "Return"), "\n",
         submit('imageDel', "Confirm"),
         hidden('studentName'),
         hidden('View user settings'),
         hidden('imageToDelete'),
         end_form;
}

# Function: display_change_profile_image_form
# Display the form for user to change his profile image
# They just have to click on the button underneath the image they want to change it to
#
sub display_change_profile_image_form {
   my @photos = glob ("$students_dir/$username/photo*");
   if (@photos == 0) {
      print h1("No images available");
      return;
   }
   print h1("To change profile image: Click on the button underneath the image you want to change it to");
   print p, start_form;
   my @photoNames = (); # array containing photo names
   foreach my $photoNumber (0..$#photos) {
      print "\n<img src='$photos[$photoNumber]'>\n";
      $photos[$photoNumber] =~ s/$students_dir\/$username\///; # remove the directory path
      push (@photoNames, $photos[$photoNumber]);
      if ($photoNumber % 5 == 4) {  # after every row of images, print the names underneath
         print p;
         foreach my $photoName (@photoNames) {
            print "<input type='submit' name='swapProfileImage' value='$photoName' style='height:30px; width:250px' />\n";
         }
         print p;
         @photoNames = (); # reset the array for new list of photonames to print
      }  
   }
   print p;
   while (@photoNames > 0) { # if we still have names to print, print the rest out.
      my $photoName = shift (@photoNames);
      print "<input type='submit' name='swapProfileImage' value='$photoName' style='height:30px; width:250px' />\n";
   }
   
   print hidden('studentName'),
         hidden('View user settings'),
         end_form;
}

# Function: display_edit_preferences_form
# Displays form so user can edit their preferences
# Fields that are editted: Gender, height, weight, age, hair colour.
#
sub display_edit_preferences_form {
   my %preferences = fill_preferences_hash();
   # start form
   print p, start_form, h1("Edit preferences: "), p, "<b1>Gender: ";
   
   # print gender
   if ($preferences{'gender'} eq "female") {    # have female checked
      print "<input type='radio' name='gender' value='female' checked='checked'> Female",
            "<input type='radio' name='gender' value='male'> Male";
   } elsif ($preferences{'gender'} eq "male") { # have male checked
      print "<input type='radio' name='gender' value='female'> Female",
            "<input type='radio' name='gender' value='male' checked='checked'> Male";
   } else {                                     # both unchecked.
      print "<input type='radio' name='gender' value='female'> Female",
            "<input type='radio' name='gender' value='male'> Male";
   }
   
   # print hair colour
   print p, "<b1>Hair colours: ", p "<b2><textarea rows='4' cols='20' name='hair colour'>$preferences{'hair_colour'}</textarea>", p,
   
   # print age
      "<b1>Age [min][max]: <textarea rows='1' cols='5' name='ageMin'>$preferences{'age'}{'min'}</textarea>\n",
      "<textarea rows='1' cols='5' name='ageMax'>$preferences{'age'}{'max'}</textarea>", p,
   # print weight
      "<b1>Weight(kg) [min][max] : <textarea rows='1' cols='5' name='weightMin'>$preferences{'weight'}{'min'}</textarea>\n",
      "<textarea rows='1' cols='5' name='weightMax'>$preferences{'weight'}{'max'}</textarea>", p,
   # print height
      "<b1>Height(m) [min][max]: <textarea rows='1' cols='5' name='heightMin'>$preferences{'height'}{'min'}</textarea>\n",
      "<textarea rows='1' cols='5' name='heightMax'>$preferences{'height'}{'max'}</textarea>", p,
   # finish form.
      hidden('studentName'), hidden('View user settings'), 
      p, submit('Change preferences'), end_form;
}

   ##################################################################
   # Main functions that are necessary for website to work properly #
   ##################################################################

# Function fill_preferences_hash
# Function which fills a hash to contain the information in preferences.txt
# This is used to create the edit_preferences_form
# Returns the hash at the end.
#
sub fill_preferences_hash {
   my %preferences = ();
   my $inBlock = 0; # tells us in we are in a block
   my $line;
   open F, "<$students_dir/$username/preferences.txt" or die "Unable to open '$students_dir/$username/preferences.txt': $!\n";
   while ($line = <F>) {
      if ($inBlock) {
         if ($line =~ /^\s/) { # leading spaces, add to hash
            $line =~ s/^\s//;
            $line =~ s/\s$//;
            chomp $line;
            # append onto list with newline cause there can be more than once preference for hair colour
            $preferences{$interest} .= "$line\n" if ($interest eq "hair_colour");
            $preferences{$interest} = $line if ($interest eq "gender"); # just the value, cause it's either female or male.
         } else {
            $inBlock = 0;
         }
      }
      if ($line =~ /^hair_colour/ || $line =~ /^gender:/) {
         $interest = $&;            # set $interest to be hair_colour or gender
         $interest =~ s/:$//;
         chomp $interest;
         $inBlock = 1; # set it to start reading in block
      } elsif ($line =~ /^weight:/ || $line =~ /^age:/ || $line =~ /^height:/) {
         $interest = $&;
         $interest =~ s/:$//;
         my $min; # for some reason we have to localize outside of loop
         my $max;
         
         foreach (0..1) { # run this twice. once for min. other time for max.
            $line = <F>;
            $min = <F> if $line =~ /min/; # set value of min with next line
            $max = <F> if $line =~ /max/; # set value of max with next line
         }
         $min =~ s/[^0-9]//g; #remove all non-digit characters
         $max =~ s/[^0-9]//g;
         $preferences{$interest}{'min'} = $min;
         $preferences{$interest}{'max'} = $max;
      }
   }
   close F;
   return %preferences;
}

# Function: login_checker
# Checks if username matches in suspended or non-supended students directory
#
sub login_checker {
   my $user = param("username");
   my $password = param("password");
   if (-e "$students_dir/$user" && $user ne "") { # check if username exists, and is not an empty string
      authenticate ("$students_dir/$user", $password);
   } elsif (-e "$suspended_students_dir/$user" && $user ne "") {
      authenticate ("$suspended_students_dir/$user", $password);
   } else {
      print "Invalid username\n";
   }
}

# Function: find_match
# Calculate the best match for the student
# Does this by going through each of the lines in preferences.txt
# And finding the category of interest (weight, hair colour etc)
# Then reading against the appropriate element in the stuDetails hash
# Will read each of the lines afterwards unless it's weight, height or age.
# If it's weight, height or age: checks all values between min and max
# All of the usernames in the stuDetails hash that were called gets an increase in their matchScore
# 
sub find_match {
   fill_matches_hash(); # first fill the hash to check who matches the student's preferences
   my $studentName = param('studentName');
   my $studentDirectory = "$students_dir/$studentName";
   if (-e "$studentDirectory/preferences.txt" == 0) {# if preferences.txt doesn't exist.
      print "No preferences provided.";
      return;
   }
   open F, "<$studentDirectory/preferences.txt" or die "unable to open '$studentDirectory/preferences.txt'";
   my $line;
   my $interest;
   my %providedPrefs = (  "age" => "0",
                          "weight" => "0",
                          "height" => "0" ); # hash which says what prefs have been taken into account for matchScore
   while ($line = <F>) {
      if ($line =~ /^hair_colour/ || $line =~ /^gender:/) {
         $interest = $&;            # set $interest to be hair_colour or gender
         $interest =~ s/:$//;
         while ($line = <F>) {         # continue reading lines 
            last if ($line !~ /^\s/);  # until we go to a line without leading space
            $line =~ s/^\s//;
            $line =~ s/\s$//;
            foreach my $student (@{$stuDetails{$interest}{$line}}) {  # go through each username in the appropriate array
               $matchScore{$student} += 10;                               # increase their matchscore
            }
         }
      }
      last if ! defined $line; # if we are already at end of file exit. to avoid warnings
      if ($line =~ /^weight:/ || $line =~ /^age:/ || $line =~ /^height:/) {
         $interest = $&;
         $interest =~ s/:$//;
         my $min; # for some reason we have to localize outside of loop
         my $max;
         my $lineCount = 0;
         while ($lineCount < 2) {
            $line = <F>;
            $min = <F> if $line =~ /min/; # set value of min with next line
            $max = <F> if $line =~ /max/; # set value of max with next line
            $lineCount++;
         }
         $min =~ s/[^0-9]//g; #remove all non-digit characters
         $max =~ s/[^0-9]//g;
         foreach my $number ($min..$max) { # go through each of the numbers from min to max
            foreach my $student (@{$stuDetails{$interest}{$number}}) {  # go through each username in the appropriate array
               $matchScore{$student} += 10;                              # increase their matchscore
            }
         }
         $providedPrefs{$interest} = 1; # set the preference as checked already
      }
   }
   
   close F;
   # finished reading preferences.txt, check for other possible commonalities involving age, weight or height
   foreach $key (keys %providedPrefs) {
      if ($providedPrefs{$key} == 0) {
         my $feature = getDetail ($key);
         $feature = getDetail ("birthdate") if ($key eq "age");
         next if ($feature == 0);
         foreach $number ($feature-10..$feature+10) { # look for people with about the same age, weight and/or height
            foreach my $student (@{$stuDetails{$key}{$number}}) {
               $matchScore{$student} += 5;                                 
            }
         }
      }
   }
   
   check_commonalities();
   
   # remove same gender from appearing in match list
   my $gender = getDetail ("gender");
   foreach my $student (@{$stuDetails{'gender'}{$gender}}) {
      $matchScore{$student} -= 499;          
   }
   
   # try to reduce age mismatches
   my $age = getDetail ("birthdate");
   foreach my $student (keys %matchScore) {
      my $ageDiff = abs(getDetail ("birthdate", $student) - $age);
      $matchScore{$student} -= (2 * int($ageDiff / 15)) if ($ageDiff > 15);    # reduce score by two * every 15 year gap
   }
   # remove yourself from appearing in match list
   $matchScore{$studentName} -= 499;
}

# Function: check_commonalities
# Adds a point for every commonality (e.g. likes same movie, book, TV show, etc)
#
sub check_commonalities {
   my $studentName = param("studentName");
   my $studentDirectory = "$students_dir/$studentName";
   open F, "<$studentDirectory/profile.txt" or die "unable to open '$studentDirectory/profile.txt'";
   my $line;
   my $interest;
   my $insideBlock = 0; # variable which tells us if we are inside a category block
   while ($line = <F>) {
      if ($insideBlock) {
         if ($line =~ /^\s/) { # if there's any leading spaces then it's still inside block
            $line =~ s/^\s//;
            $line =~ s/\s$//;
            chomp $line;
            foreach my $student (@{$stuDetails{$interest}{$line}}) {  # go through each username in the appropriate array
               $matchScore{$student} += 4;                               # increase their matchscore
            }
         } else {
            $insideBlock = 0;
         }
      }
      if ($line =~ /^\w*s:\s*$/ && $line !~ /^courses:/) { # things that have multiple likes (favourite movies, books etc.)
         $interest = $&;
         $interest =~ s/:\s*$//;    # remove the colon
         chomp $interest;           # remove newline
         $insideBlock = 1;
      }
   }
}

# Function: fill_matches_hash
# Function which fills the hash with an array of the possible
# Hobbies, interest and details about weight, hair_colour, gender, height and age.
#
sub fill_matches_hash {
   foreach my $subdirectory (glob "$students_dir/*") {
      open F, "<$subdirectory/profile.txt" or next;
      my $user = $subdirectory;
      $user =~ s/.*\///;
      my $line;
      my $interest;
      my $insideBlock = 0;
      while ($line = <F>) {
         if ($insideBlock) {
            $insideBlock = 0 if ($line !~ /^\s/); # if there are no leading spaces then it's not inside block
            if ($line =~ /^\s/) {
               $line =~ s/^\s*//;      # remove leading spaces
               $line =~ s/\s$//;       # remove trailing spaces
               chomp $line;            # remove new line
               push (@{$stuDetails{$interest}{$line}}, $user);
            }
         }
         if ($line =~ /^\w*s:\s*$/ && $line !~ /^courses:/) { # things that have multiple likes (favourite movies, books etc.)
            $interest = $&;
            $interest =~ s/:\s*$//;    # remove the colon
            chomp $interest;
            $insideBlock = 1;
         }
         if ($line =~ /^weight:/ || $line =~ /^hair_colour:/ || $line =~ /^gender:/ || $line =~ /^height:/) {
            $interest = $&;         # set $interest to the category to look under in $stuDetails
            $interest =~ s/:\s*$//;    # remove the colon
            $line = <F>;            # iterate to next line, so now $line contains actual interest (not just category)
            $line =~ s/^\s*//;      # remove leading spaces
            $line =~ s/\s$//;       # remove trailing spaces
            chomp $line;            # remove new line
            $line =~ s/[^0-9]//g if ($interest eq "height" || $interest eq "weight"); # remove the units from number
            push (@{$stuDetails{$interest}{$line}}, $user);   # add onto array
         } elsif ($line =~ /^birthdate:/) {                          # if it is birthdate, have to calculate ags
            $interest = "age";
            $line = <F>;
            my $age = calculate_age ($line);                      # find out ages
            push (@{$stuDetails{$interest}{$age}}, $user);    # then add it onto array
         }
      }
      close F;
   }
}

# Function: send_verification_mail
# Function which checks if username has not been taken and then 
# Sends a verification email to the email address provided if not taken
# Creates the student inside the $unactivated_students_dir, to be moved later when verification link has been gone to
# Verification link will fill open the script with 'activate' parameter containing "username,pass,email"
# Separated by one dot and nothing else (in that order).
#
sub send_verification_mail {
   my $desiredUser = param("createUser");
   my $desiredPass = param("createPass");
   my $desiredEmail = param("createEmail");
   my $correctDetails = 1;
   
   if (userToIndex ($desiredUser, 0) != -1 || isSuspended ($desiredUser)) { # username already exists in either directories
      print "Username already exists please try a different one.\n";
      $correctDetails = 0;
   } elsif ($desiredUser !~ /^[0-9A-Z]*$/i) {
      print "Username should only contain numbers and letters, please try again";
      $correctDetails = 0;
   } elsif ($desiredUser eq "" || $desiredPass eq "" || $desiredEmail eq "") {
      print "Please fill in all fields.";
      $correctDetails = 0;
   } elsif ($desiredEmail !~ /^[0-9a-zA-z_\.\-]+@[0-9a-zA-z_\.\-]+$/) {
      print "Please enter a valid email";
      $correctDetails = 0;
   }
   
   if ($correctDetails == 0) {
      print p, start_form, submit ('Create account', "Retry"), end_form;
      return;
   } elsif ($correctDetails) {
      # Otherwise we can now temporarily make the file and send verification mail as username is not taken
      my $encryptedNumber = encrypt ($desiredUser);
      mkdir ("$unactivated_students_dir") if (-d "$unactivated_students_dir" == 0); # make the unactivated students folder if it doesn't exist.
      my $newDirectory = "$unactivated_students_dir/$encryptedNumber"; # store new directory into a single string for convenience
      mkdir ("$newDirectory"); # make the directory
      open (NEW, '>', "$newDirectory/profile.txt"), or die "Unable to open '$newDirectory/profile.txt': $!\n";
      print NEW "username:\n\t$desiredUser\npassword:\n\t$desiredPass\nemail:\n\t$desiredEmail\n"; # fill in profile.txt with user,pass and email
      close NEW;
      open (PREF, '>', "$newDirectory/preferences.txt"), or die "Unable to open '$newDirectory/preferences.txt': $!\n";
      close PREF;
      
      # Write up message and send
      my $verificationLink = "$ENV{'SCRIPT_URI'}?activate=$encryptedNumber";
      my $message = "Hello, 
                     You have registered for an account for LOVE2041 under these details: 
                     
                     username: $desiredUser
                     password: $desiredPass
                     email: $desiredEmail
                     
                     Please copy and paste the following link to complete the registration of your account.
                     $verificationLink
                     Thank you.
                     
                     Kind Regards from,
                     
                     The person who the site, duh.
                     
                     This email was automatically sent by LOVE2041 Perl Script. Please do not reply.\n";

      # send email 
      send_email (param("createEmail"), 'thebestofthebest@love2041.com', 'LOVE2041: Verification email', $message);
      
      print "Verification email sent to given email address.\n";
      print p, start_form, submit ('Logout', "Return"), end_form;
   }
}

# Function: create_account
# Moves the folders from the needs_verification folder into students
# And changes the name
# Then prints a message saying redirecting and redirects after a small delay
# 
sub create_account {
   my $encryptedNumber = param("activate");
   if (-e "$unactivated_students_dir/$encryptedNumber" == 0) { # if the file no longer exists
      print "Sorry verification link has expired\n";
      return;
   }
   
   # otherwise just move the files over.
   my $moveFrom = "$unactivated_students_dir/$encryptedNumber/";
   my $moveTo = "$students_dir/$encryptedNumber/";
   move ($moveFrom, $moveTo);
   
   # rename the folder
   my $user = getDetail ("username", $encryptedNumber);
   rename ("$students_dir/$encryptedNumber/", "$students_dir/$user/");
   
   # print success message to user and redirect.
   my $redirect_url = "$ENV{'SCRIPT_URI'}";
   print h1("Account has been created.. redirecting to login screen..\n");
   print "<META http-equiv=\"refresh\" content=\"4;URL=$redirect_url\">"; # redirect user after 4 second delay
}

# Function: send_mail_to_change_password
# Sends the user an e-mail to change their password
# E-mail contains a link for the user to set a new password
#
sub send_mail_to_change_password {
   my $user = param ("forgotPass"); # username of account with the forgotten password
   # first check user actually exists.
   if ($user eq "") {
      print "Please fill in all fields\n";
      print p, start_form, submit('Forgot password', Return), end_form;
      return;
   }
   my $n = userToIndex($user, 1);
   if ($n == -1) {         # findUser will return -1 if invalid username is specified
      print "User '$user' not found. Please try again. Username may be case sensitive.";
      print p, start_form, submit('Forgot password', Return), end_form;
      return;              # exit function, so it won't print anything else.
   }
   # okay so username exists.
   my $email = getDetail ("email", $user); # get the email address of the provided user
   my $encryptedNumber = encrypt($user);
   my $passChangeLink = "$ENV{'SCRIPT_URI'}?passChange=$encryptedNumber";
   my $message = "Hello, 
                  You have requested a password change for your account, $user.
                  
                  Please copy and paste the following link if you wish to continue with the password change.
                  $passChangeLink
                  Thank you.
                  
                  Kind Regards from,
                  
                  The person who the site, duh.
                  
                  This email was automatically sent by LOVE2041 Perl Script. Please do not reply.\n";

   send_email($email, 'thebestofthebest@love2041.com', 'LOVE2041: Password change', $message);
   print "Sent mail to the provided user's email address to restore password. Please check your email.";
   print p, start_form, submit ('Logout', "Return"), end_form;
}

# Function: send_message
# Sends a message to the user that was clicked on and prints a message saying sent.
#
sub send_message {
   send_email (param('to'), "thebestofthebest\@love2041.com", param ('subject'), param ('message'));
   print h1("Message sent to user's email.");
}

# Function: change_password
# Function changes the password in the user's profile.txt by creating new array with profile.txt and filling it
# Input 1: Scalar string containing new password
# Input 2: Scalar string containing the encrypted version of the account's name whose password we are changing
# Input 3: Scalar string containing the other field containing new password (need to confirm they are the same)
# Input 4: Optional input which tells us the oldPassword, only used when changing password when already logged in.
#

sub change_password ($$$$) {
   my $newPassword = $_[0];
   my $Encrypteduser = $_[1];
   my $user = "";
   foreach my $student (@studentNames) {
      if ($Encrypteduser == encrypt($student)) { # if this is true then user exists, and set $user
         $user = $student;
         last;
      }
   }
   my $confirmPassword = $_[2];
   my $oldPassword = $_[3] if (@_ == 4); 
   
   if ($user eq "") {   # trying to hack..
      print p("Don't even try.. hax0r");
      return;
   } elsif ($newPassword ne $confirmPassword) { # if they did not match, exit.
      print p("Error: Passwords do not match");
      return;
   } elsif ($newPassword eq "" || $oldPassword eq "" || $confirmPassword eq "") {   # If any fields are blank
      print p("Please fill in all fields\n");               # Print error message
      return;
   }
   
   open READ, "<$students_dir/$user/profile.txt" or die "Failed to open '$students_dir/$user/profile.txt': $!\n";
   @newProfileTxt = <READ>; # fills array with file contents
   my $lineWithPassword = 0;
   foreach my $line (0..$#newProfileTxt) { # go through file, until it reaches password line
      if ($newProfileTxt[$line] =~ /^password:/) { 
         if (@_ == 4) { # if there are 3 parameter inputs, then we need to check password before changing
            my $currentPassword = $newProfileTxt[$line + 1];
            $currentPassword =~ s/^\s*//;             # remove leading white space
            $currentPassword =~ s/\s*$//;             # remove trailing white space
            chomp $currentPassword;                   # remove new line character
            if ($currentPassword ne $oldPassword) {   # if it doesn't match then exit
               print p("Current password incorrect. Please try again.\n");
               return;
            }                                         # otherwise it will just continue, and change password.
         }
         $newProfileTxt[$line + 1] = "\t$newPassword\n"; # change the next line to newpassword
         last;
      }
   }
   close READ;
   
   # New profile.txt has been created, now write it into the file.
   open (WRITE, '>', "$students_dir/$user/profile.txt") or die "Failed to open '$students_dir/$user/profile.txt': $!\n";
   print WRITE join ('', @newProfileTxt); # writes to file
   close WRITE;
   
   my $redirect_url = "$ENV{'SCRIPT_URI'}";
   print h1("Password was changed successfully. Redirecting to login page..") if (@_ != 4); # was not logged in
   print h1("Password was changed successfully. Redirecting to login page.. Please login again") if (@_ == 4); # was logged in
   print "<META http-equiv=\"refresh\" content=\"4;URL=$redirect_url\">"; # redirect user after 4 second delay
}

# Function: change_profile_description
# Access profile.txt
# Erase everything from Additional information and afterwards.
# Replace it with the input that user gave and store it into array.
# Replace profile.txt with newProfileTxt array
#
sub change_profile_description {
   $newProfileDescription = param('Extra info');
   $newProfileDescription =~ s/^\s//g; # remove leading new line if there is.
   $newProfileDescription =~ s/\n/\n\t/g; # convert all newlines to newline + tab character. 
   open my $fh, "<$students_dir/$username/profile.txt" or die "Unable to open '$students_dir/$username/profile.txt': $!";
   my @newProfileTxt = <$fh>;
   close $fh;
   
   my $additionalExists = 0;
   my $extraInfo = ""; # initialize variables
   foreach $lineNumber (0..$#newProfileTxt) { # go through each line in profile.txt
      $extraInfo .= $newProfileTxt if ($additionalExists); #add onto variable if it exists
      $additionalExists = 1 if ($newProfileTxt[$lineNumber] =~ /^Additional information:/); # if profile.txt has it already..
   }
   push (@newProfileTxt, "Additional information:\n\t$newProfileDescription"); # add in the new "category"
   
   open (WRITE, '>', "$students_dir/$username/profile.txt") or die "Failed to open '$students_dir/$username/profile.txt': $!\n";
   print WRITE join ('', @newProfileTxt); # writes to file
   close WRITE;
   print h1("Successfully changed profile description. Click below to view your new profile!");
   print p, start_form, hidden ('studentName'), submit ('View your profile', 'View new profile'), end_form;
}

# Function: delete_account
# Function checks if password typed in matches the correct one
# If it is correct, then it will remove all files in student's directory
# And then remove the directory itself
#
sub delete_account {
   my $currentPassword = param("currentPassword");
   my $correctPassword = getDetail("password");
   if ($correctPassword ne $currentPassword) {
      print "Incorrect password, please try again.";
      return;
   }
   if ($currentPassword eq "") {
      print "Please fill in all the fields.";
      return;
   }
   my @filesToDelete = glob("$students_dir/$username/*");
   unlink @filesToDelete;
   rmdir ("$students_dir/$username/");
   print h1("Account deleted. Now logging off..");
   print "<META http-equiv=\"refresh\" content=\"4;URL=$ENV{'SCRIPT_URI'}\">"; # redirect user after 4 second delay
}

# Function: suspend_account
# Function checks if password typed in matches the correct one
# If it is correct, then it will then move all the files over to a different folder containing suspended_students
#
sub suspend_account {
   my $currentPassword = param("currentPassword");
   my $correctPassword = getDetail("password");
   if ($correctPassword ne $currentPassword) {
      print "Incorrect password, please try again.";
      return;
   }
   if ($currentPassword eq "") {
      print "Please fill in all the fields.";
      return;
   }
   # password is correct, move folder to suspended_students directory.
   my $moveFrom = "$students_dir/$username/";
   mkdir ($suspended_students_dir) if (-d "$suspended_students_dir" == 0); # make the directory if it doesn't exist.
   my $moveTo = "$suspended_students_dir/$username/";
   move($moveFrom, $moveTo);
   
   print h1("Account has been suspended. Logging out now..");
   print "<META http-equiv=\"refresh\" content=\"4;URL=$ENV{'SCRIPT_URI'}\">"; # redirect user after 4 second delay
}

# Function: activate_account
# Move all the files back to the students directory.
#
sub activate_account {
   my $moveFrom = "$suspended_students_dir/$username/";
   my $moveTo = "$students_dir/$username/";
   
   move($moveFrom, $moveTo);
   
   print toolbar();
   print h1("Account has been re-activated!");
   print display_sets(0);
   
}

# Function upload_image
# Upload the image into students directory
# 
sub upload_image {
   my $imageToUpload = param('filename');
   if ($imageToUpload eq "") {
      print "Please select a file";
      return;
   }
   my @photos = glob ("$students_dir/$username/photo*"); # used to figure out what to name the file.
   my $photoCount = ""; # store the photo??.jpg value
   foreach my $photoNumber (0..$#photos) { # loop to find lowest number
      my $photoName = $photos[$photoNumber];
      $photoName =~ s/$students_dir\/$username\///;
      $photoNumber =~ s/^(.)$/0$1/ if ($photoNumber < 10); # add a 0 to the front if it is less than ten.
      if ($photoName !~ /$photoNumber/) { # if the number is not in the name then it means that photo?? currently doesn't exist.
         $photoCount = $photoNumber;
         last;
      }
   }
   $photoCount = @photos if ($photoCount eq ""); # if all correct, then it's just equal to the size.
   $photoCount =~ s/^(.)$/0$1/ if ($photoCount < 10); # add a 0 to the front if it is less than ten.
   my $directoryToUpload = "$students_dir/$username/photo$photoCount.jpg";
   open (FILE, '>', "$directoryToUpload") or die "Failed to upload to: '$students_dir/$username': $!\n";
   print FILE foreach (<$imageToUpload>); # print to the file every line in the filehandle of the image.
   close FILE;
   
   `convert $directoryToUpload -resize 250x250! $directoryToUpload`; # run a shell command to convert image size cause we are allowed.
   print "Uploaded file: ", p;
   print "<img src='$directoryToUpload'>\n"; 
}

# Function delete_image
# Delete the image given from user's profile
# Input 1: Name of the image to delete
#
sub delete_image ($) {
   my $imageNameToDelete = $_[0];
   unlink ("$students_dir/$username/$imageNameToDelete") or die "Failed to delete $imageNameToDelete: $!";
   print h1("Successfully deleted $imageNameToDelete\n");
}

# Function: change_profile_image
# Swaps the chosen photo* with profile.jpg
# Checks if profile.jpg exists first, then if it does,
# It swaps the images through the use of a temporary file buffer
#
sub change_profile_image ($) {
   my $newProfileJPG = param('swapProfileImage');
   $newProfileJPG = "$students_dir/$username/$newProfileJPG"; # add the path to the variable
   my $tempFile = "$students_dir/$username/photo.jpg.temp"; # temp file
   my $currentProfileJPG = "$students_dir/$username/profile.jpg";
   
   if (-e "$currentProfileJPG" == 0) { # if profile.jpg doesn't exist, just move the chosen image to profile.jpg
      copy ($newProfileJPG, $currentProfileJPG); # no need to go through a buffer.
      unlink ($newProfileJPG); # remove old photo*
   } else { # if it does exist, need a buffer
      # First store all contents of  $newProfileJPG into the temp file.
      copy ($newProfileJPG, $tempFile);
      unlink($newProfileJPG); # remove it just incase
      
      # Then store all contents of the current profileJPG into $newProfileJPG
      copy ($currentProfileJPG, $newProfileJPG);
      unlink ($currentProfileJPG); # remove it just incase
      
      # Then store all contents from temp file into the current profile.jpg
      copy ($tempFile, $currentProfileJPG);
      
      # Finally remove the temp file
      unlink ($tempFile);
   }
   
   # Print a message to say job done
   print "Profile image changed to: ", p,
      "<img src='$currentProfileJPG'>\n";
}

# Function: change_preferences
# Edit preferences.txt with new preferences.
#
sub change_preferences {
   open (F, '>', "$students_dir/$username/preferences.txt") or die "Unable to open $students_dir/$username/preferences.txt: $!";
   if (param('gender') ne "") {
      my $gender = param('gender');
      print F "gender:\n\t$gender\n";
   }
   if (param('hair colour') ne "") {
      my $hairColour = param('hair colour');
      chomp $hairColour;
      my @hairColours = split '\n', $hairColour;
      print F "hair_colours:\n\t";
      my $lineCount = 0;
      foreach $color (@hairColours) {
         print F "$color\n";
         print F "\t" if ($lineCount != $#hairColours); # print a tab char if not at last line
         $lineCount++;
      }
   }
   if (param('ageMin') ne "" && param('ageMax') ne "") {
      my $ageMin = param('ageMin');
      my $ageMax = param('ageMax');
      print F "age:\n\tmin:\n\t\t$ageMin\n\tmax:\n\t\t$ageMax\n";
   }
   if (param('weightMin') ne "" && param('weightMax') ne "") {
      my $weightMin = param('weightMin');
      my $weightMax = param('weightMax');
      print F "age:\n\tmin:\n\t\t$weightMin\n\tmax:\n\t\t$weightMax\n";
   }
   if (param('heightMin') ne "" && param('heightMax') ne "") {
      my $heightMin = param('heightMin');
      my $heightMax = param('heightMax'); 
      print F "age:\n\tmin:\n\t\t$heightMin\n\tmax:\n\t\t$heightMax\n";
   }
   print h1("Preferences changed successfully\n");
   close F;
}

   ##########################
   # Small helper functions #
   ##########################
   
# Function: userToIndex
# Function reads through array of studentNames and tries to find the $searchUser term
# returns index in array if found, otherwise returns -1
# Input 1: A scalar containing a string of the username, not case sensitive
# Input 2: A scalar boolean saying whether it should be a case sensitive search or not (1 = true, 0 = false)
#
sub userToIndex ($$) {
   my $searchUser = $_[0];
   my $caseSensitive = $_[1];
   my $count = 0;
   if ($caseSensitive) {
       foreach my $studentName (@studentNames) {
         last if ($studentName =~ /^$searchUser$/);
         $count++;
      }
   } else {
      foreach my $studentName (@studentNames) {
         last if ($studentName =~ /^$searchUser$/i);
         $count++;
      }
   }
   $count = -1 if ($count == @studentNames); #if we reach the end and not found, then set count to -1
   return $count;
}

# Function: calculate_age
# Find out the age given the birthdate
# Not too precise, as it gives the age that they will turn this year
# Input 1: Birthdate taken from profile.txt
#
sub calculate_age ($){
   my $birthdate = $_[0];
   my $currYear = 2014;
   $birthdate =~ /(\d{4})/;
   my $birthYear = $1; # reads in the year, as it is the only one with 4 consecutive numbers
   my $age = $currYear - $birthYear; #calculate age
   return $age;
}

# Function: getDetail
# Search for a detail for the student currently logged in
# Only works for one line details (height, weight, birthdate, etc)
# Returns age if searchTerm was "birthdate"
# Function returns 0 if the detail was not found
# Input 1: Scalar string containing detail to be searched
# Input 2: Optional (Should only be necessary when not logged in, i.e. forgot password).. contains the username to search in
#
sub getDetail ($$) {
   my $studentName = param('studentName');
   $studentName = $_[1] if (@_ == 2); # Will be input 2 if provided.
   my $searchTerm = $_[0];
   my $lineCount = 0;
   my $detail;
   open FILE, "<$students_dir/$studentName/profile.txt" or die "failed to open $students_dir/$studentName: $!\n";
   my @lines = <FILE>;
      foreach my $line (0..$#lines) {
         if ($lines[$line] =~ /^$searchTerm/) {
            $lineCount = $line + 1;
            last;
         }
      }
   close FILE;
   if ($lineCount == 0) { # if the term was not found
      $detail = 0;
   } elsif ($searchTerm eq "birthdate") {  # if we were looking for birthdate, convert to age
      $detail = calculate_age ($lines[$lineCount]);
   } else {
      $detail = $lines[$lineCount];
      if ($searchTerm eq "height" || $searchTerm eq "weight") { # only want numbers for height and weight
         $detail =~ s/[^0-9]//g;
      }
      $detail =~ s/^\s//g; # remove leading white space
      $detail =~ s/\s$//g; # remove trailing white space
      chomp $detail;
   }
   return $detail;
}

# Function: userSearch
# Searches through studentNames array for usernames matching its input
# Return a list of all matching usernames
# Input 1: a scalar containing a substring of a username
#
sub userSearch ($) {
   my $searchTerm = $_[0];
   my @searchList = ();
   foreach my $studentName (@studentNames) {
      push (@searchList, $studentName) if ($studentName =~ /$searchTerm/i);
   }
   return @searchList;
}

# Function: information_filter
# Function to remove name, email, password and courses taken from profile page
# Input 1: Scalar string containing the directory to access profile.txt of a certain user
# 
sub information_filter ($) {
   my $profile_filename = $_[0];
   open my $p, "$profile_filename" or die "can not open $profile_filename: $!";
   my @details = <$p>;
   my $remove = 0; # variable which says whether to remove current line or not
   foreach my $line (@details) {  # go through each of the lines
      if ($line =~ /^courses:\s*$/ || $line =~ /^email:\s*$/ || $line =~ /^password:\s*$/ ||
         $line =~ /^name:\s*$/) { # if it contains any of the details we want to remove
         $remove = 1;             # set variable ($remove) to true
         $line = "";              # remove current line
         next;
      }
      if ($remove) {              # if $remove is true then we check if line has leading spaces
         if ($line =~ /^\s+/) {   # if it has leading spaces
            $line = "";           # remove all lines inside block
         } else {
            $remove = 0;          # otherwise we are in another block, set $remove to false
         }
      }
   }
   close $p;
   return @details;
}

# Function: isSuspended
# Checks whether the username of a person is in the suspended_students directory
# Returns 1 if it exists in the directory, or 0 otherwise.
# Input 1: Scalar string containing the username we are searching for.
#
sub isSuspended ($) {
   my $searchTerm = $_[0];
   my @suspended = glob ("$suspended_students_dir/*");
   foreach my $student (@studentNames) {
      $student =~ s/$suspended_students_dir\///;   #remove the directory path from name
      if ($student =~ /^searchTerm$/i) {
         return 1;
      }
   }
   return 0; # if gone through all students and none match, then it's not in the directory.
}

# Function: authenticate
# Checks if password matches with inputted one
# If it matches, it goes to the display_sets page.
# Input 1: Scalar string containing directory to find password
# Input 2: Scalar string containing typed in password (input password)
#
sub authenticate ($$) {
   my $userDirectory = $_[0];
   my $inSuspended = $userDirectory =~ /suspended/; # if we find "suspended" in $userDirectory then it is true, else false.
   my $password = $_[1];
   open FILE, "<$userDirectory/profile.txt" or die "Failed to open '$userDirectory': $!\n";
   my @lines = <FILE>;
   my $count = 0; 
   foreach my $line (@lines) {
      $count++;
      last if ($line =~ /^password:\s*$/); # break out of loop when it reaches password line
   }
   my $correctPassword = $lines[$count]; # since we incremented count before if statement, count contains lineNumber of the actual password
   $correctPassword =~ s/\s*$//g;        # remove trailing white space
   $correctPassword =~ s/^\s*//g;        # remove leading white space
   if ($password eq $correctPassword) {  # check if password is correct
      if ($inSuspended == 0) {           # if we aren't in suspended directory.
         print toolbar();
         print display_sets(0);
      } else {                           # if we are.. then we check if user wants to activate account again.
         print h1("Your account is currently suspended. Do you want to re-activate it?");
         print p, start_form, submit ('Reactivate account'), submit ('Logout', "Go back"), hidden ('studentName'), end_form; #got bad feeling bout this
      }
   } else {                              # if wrong, then print invalid password
      print "Invalid password!\n";
   }
}

# Function: encrypt
# Takes in a string and encrypts, kind of like hashing 
# Returns a number, used for verification links sent to email
# Input 1: String to encrypt
#
sub encrypt ($) {
   my $stringToEncrypt = $_[0];
   my $encryptedValue = 0;
   my @chars = split ('', $stringToEncrypt); # separate the string into characters
   foreach my $charIndex (0..$#chars) {
      $encryptedValue += 3923095;
      $encryptedValue -= $charIndex * 1337;
      $encryptedValue += (ord($chars[$charIndex]) * @chars);
   }
   return $encryptedValue;
}

# Function: send_email
# Function to send a mail
# Code taken from http://www.tutorialspoint.com/perl/perl_sending_email.htm
# Input 1: To
# Input 2: From
# Input 3: Subject
# Input 4: Message
#
sub send_email ($$$$) {
   my $to = $_[0];
   my $from = $_[1];
   my $subject = $_[2];
   my $message = $_[3];
   
   open(MAIL, "|/usr/sbin/sendmail -t");
 
   # Email Header
   print MAIL "To: $to\n";
   print MAIL "From: $from\n";
   print MAIL "Subject: $subject\n\n";
   # Email Body
   print MAIL $message;

   close(MAIL);
}

# Function: display_matching_algo
# Prints out how matching works.
#
sub display_matching_algo {
   print h1(pre("
   Matching preference, +10.
   Similar age, height, weight, +5
   Common likes, +4
   Age gap > 15, -2 for every 15 years age gap."));
}
