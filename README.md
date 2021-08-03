# call_content_for_autoarchive
Simple python script to call the content api to add a list of courses to the automatic archive queue.

developed by jeff.kelley@blackboard.com  June 2021
This is unsupported and without warranty


To add a set of course IDs to the automatic archive list
this script makes a simple call to the content API for a csv list of course IDs.
The result is an entry in the course_registry table for that course PK1.

  course_registry.registry_key = last access by un-enrolled admin
  course_registry.registry_value = 2021-06-21 11:37:27.448


logic..
  -  Authenticate to get token
  - Itterate through the list of courses from the CSV file
     - For each course, call the content API
  - Log the process


Usage...  >python Call_content_for_archives.py <properties file> <course id csv file>
will generate a log file output
