#!/bin/bash

#set exit-on-error mode
set -e
#trap the exit signal instead of error(ERR) and handle it
#$? contains exit status of the last command executed
trap 'catch $? $LINENO' EXIT

#function to catch the exit signal and handle the exception
function catch() {
  #echo "catching EXIT!"
  if [ "$1" != "0" ]; then
    #error handling goes here
    #echo "Error $1 occurred on $2"
    #total_score=0
    echo "Marks scored: $total_score"
    remarks="EXCEPTION! Your code ran into an error! Debug your code."
    echo "Remarks: $remarks"
    #check whether temporary generated out.txt file exists or not
    [ -f out.txt ]
    if [ "$?" = 0 ]; then
      #delete the temporary generated out.txt file
      #echo "Return Code: $?, File out.txt exists!"
      rm -f out.txt
    else
      echo "Something went wrong, run this file again!"
      exit 1
    fi
  fi
}

#function to evaluate the student submitted file
function evaluate() {
  #run the student submitted file ($2) against the test_file ($3)
  #and generate temporary out.txt file
  if [ -f store.txt ]; then
    rm -f store.txt
  fi
  
  #run 'storeInfo' function in the student submitted file
  while IFS= read -r line; do
    read -a test_case <<< "$line"
    name="${test_case[0]}"
    value="${test_case[1]}"
    bash "$2" storeInfo "$name" "$value"
  done < "$3"
  
  if [ "$?" = 0 ]; then
    if [ -f store.txt ]; then

      # ================================= #

      while IFS= read -r line; do
        read -a test_case <<< "$line"
        name_timestamp="${test_case[0]}"
        value="${test_case[1]}"
        name=$(echo "$name_timestamp" | awk -F'_' '{print $1}')
        echo "$name $value" >> storeInfo_out.txt
      done < store.txt

      max_lines_to_match=$(wc -l < "$ideal_storeInfo_output_file")
      # echo "max_lines_to_match: $max_lines_to_match"
      line_match_weightage=$(echo "scale=2;$storeInfo_weightage/$max_lines_to_match" | bc -l)
      #echo "line_match_weightage: $line_match_weightage"

      num_lines_mismatch=$(( ( $(diff storeInfo_out.txt "$ideal_storeInfo_output_file" | wc -l) - 2 ) / 2 ))
      if [ "$num_lines_mismatch" -lt 0 ]; then
        num_lines_mismatch=0
      fi
      echo "num_lines_mismatch: $num_lines_mismatch"

      if [ $num_lines_mismatch -eq 0 ]; then
        total_score=$(echo "scale=2;$total_score+$storeInfo_weightage" | bc -l)
        echo "Score up till Test case number $(($1 + 1)) = $total_score"
      else
        total_score=$(echo "scale=2;$total_score+($storeInfo_weightage-($num_lines_mismatch*$line_match_weightage))" | bc -l)
        echo "Score up till Test case number $(($1 + 1)) = $total_score"
      fi

      # ================================= #

      #run 'displayInfo' function in the student submitted file
      bash "$2" displayInfo >> temp.txt

      while IFS= read -r line; do
        read -a test_case <<< "$line"
        name_timestamp="${test_case[0]}"
        value="${test_case[1]}"
        name=$(echo "$name_timestamp" | awk -F'_' '{print $1}')
        echo "$name $value" >> displayInfo_out.txt
      done < temp.txt
      
      rm -f temp.txt

      max_lines_to_match=$(wc -l < "$ideal_displayInfo_output_file")
      # echo "max_lines_to_match: $max_lines_to_match"
      line_match_weightage=$(echo "scale=2;$storeInfo_weightage/$max_lines_to_match" | bc -l)
      #echo "line_match_weightage: $line_match_weightage"

      num_lines_mismatch=$(( ( $(diff displayInfo_out.txt "$ideal_displayInfo_output_file" | wc -l) - 2 ) / 2 ))
      if [ "$num_lines_mismatch" -lt 0 ]; then
        num_lines_mismatch=0
      fi
      echo "num_lines_mismatch: $num_lines_mismatch"

      if [ $num_lines_mismatch -eq 0 ]; then
        total_score=$(echo "scale=2;$total_score+$storeInfo_weightage" | bc -l)
        echo "Score up till Test case number $(($1 + 1)) = $total_score"
      else
        total_score=$(echo "scale=2;$total_score+($storeInfo_weightage-($num_lines_mismatch*$line_match_weightage))" | bc -l)
        echo "Score up till Test case number $(($1 + 1)) = $total_score"
      fi

      # ================================= #

      #run 'getOrderID' function in the student submitted file
      while IFS= read -r line; do
        # read -a test_case <<< "$line"
        data=($line)
        name="${data[0]}"
        bash "$2" getOrderID "$name" >> getOrderID_out.txt
      done < "$4"

      max_lines_to_match=$(wc -l < "$ideal_getOrderID_output_file")
      # echo "max_lines_to_match: $max_lines_to_match"
      line_match_weightage=$(echo "scale=2;$getOrderID_weightage/$max_lines_to_match" | bc -l)
      #echo "line_match_weightage: $line_match_weightage"

      num_lines_mismatch=$(( ( $(diff getOrderID_out.txt "$ideal_getOrderID_output_file" | wc -l) - 2 ) / 2 ))
      if [ "$num_lines_mismatch" -lt 0 ]; then
        num_lines_mismatch=0
      fi
      echo "num_lines_mismatch: $num_lines_mismatch"

      if [ $num_lines_mismatch -eq 0 ]; then
        total_score=$(echo "scale=2;$total_score+$getOrderID_weightage" | bc -l)
        echo "Score up till Test case number $(($1 + 1)) = $total_score"
      else
        total_score=$(echo "scale=2;$total_score+($getOrderID_weightage-($num_lines_mismatch*$line_match_weightage))" | bc -l)
        echo "Score up till Test case number $(($1 + 1)) = $total_score"
      fi

      #delete the temporary generated storeInfo_out.txt file
      rm -f storeInfo_out.txt
      rm -f displayInfo_out.txt
      rm -f getOrderID_out.txt
      rm -f store.txt
    fi
  fi
}

#take the student submitted file name from input arguments
submission_file=$1

#maximum score of the problem statement
max_score=10
#to compute total marks scored after evaluation
total_score=0
#remarks to give as per the marks scored
remarks=""

#find Test TXT Files and their count
cmd_find_storeInfo_test_files=$(ls outlab2_q1_storeInfo_input**.txt)
storeInfo_test_files_list=($cmd_find_storeInfo_test_files)
#print number of all test txt files
no_of_test_cases="${#storeInfo_test_files_list[@]}"
echo "Number of Test TXT files: $no_of_test_cases"

cmd_find_getOrderID_test_files=$(ls outlab2_q1_getOrderID_input**.txt)
getOrderID_test_files_list=($cmd_find_getOrderID_test_files)

#compute the weightage of each test case
test_case_weightage=$(echo "scale=2;$max_score/$no_of_test_cases" | bc -l)
#echo $test_case_weightage

storeInfo_weightage=$(echo "scale=2;0.2*$test_case_weightage" | bc -l)
displayInfo_weightage=$(echo "scale=2;0.2*$test_case_weightage" | bc -l)
getOrderID_weightage=$(echo "scale=2;0.6*$test_case_weightage" | bc -l)

#find Ideal Output TXT Files and their count
cmd_find_ideal_storeInfo_output_files=$(ls ideal_outlab2_q1_storeInfo_output**.txt)
ideal_storeInfo_output_files_list=($cmd_find_ideal_storeInfo_output_files)

cmd_find_ideal_displayInfo_output_files=$(ls ideal_outlab2_q1_displayInfo_output**.txt)
ideal_displayInfo_output_files_list=($cmd_find_ideal_displayInfo_output_files)

cmd_find_ideal_getOrderID_output_files=$(ls ideal_outlab2_q1_getOrderID_output**.txt)
ideal_getOrderIDInfo_output_files_list=($cmd_find_ideal_getOrderID_output_files)

test_case_num=0
while [ $test_case_num -lt $no_of_test_cases ]; do
  echo "===================================="
  echo "Evaluating for Test case: $((test_case_num + 1))"

  #get the test_file name
  test_storeInfo_file="${storeInfo_test_files_list[$test_case_num]}"
  test_getOrderID_file="${getOrderID_test_files_list[$test_case_num]}"

  #get the ideal_storeInfo_output_file name
  ideal_storeInfo_output_file="${ideal_storeInfo_output_files_list[$test_case_num]}"

  #get the ideal_displayInfo_output_file name
  ideal_displayInfo_output_file="${ideal_displayInfo_output_files_list[$test_case_num]}"

  #get the ideal_getOrderID_output_file name
  ideal_getOrderID_output_file="${ideal_getOrderIDInfo_output_files_list[$test_case_num]}"

  #evaluate the student submitted file against the test_file
  #and generate temporary out.txt file
  evaluate "$test_case_num" "$submission_file" "$test_storeInfo_file" "$test_getOrderID_file"
  echo "===================================="
  #increment test_case_num variable
  test_case_num=$(($test_case_num + 1))
done

#round off the total_score to the nearest integer
total_score=$(echo "($total_score+0.5)/1" | bc)
if [ "$total_score" -lt 0 ]; then
  total_score=0
fi
echo "Marks scored: $total_score"

#provide remarks as per the total marks scored
if [ "$total_score" = $max_score ]; then
  echo "SUCCESS, Your code passed all the test cases."
  remarks="Congrats! You have successfully completed the assignment. Keep it up!"
  echo "Remarks: $remarks"
else
  echo "FAIL, Your code did not pass one or more test cases."
  remarks="Your code did not pass all of the test cases!"
  echo "Remarks: $remarks"
fi
