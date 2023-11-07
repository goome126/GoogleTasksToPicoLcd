from __future__ import print_function

import os
import serial
import time
from os import path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']

serialCon = serial.Serial('COM7', 115200, parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.SEVENBITS)


def main():
    """Shows basic usage of the Tasks API.
    Prints the title and ID of the first 10 task lists.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('tasks', 'v1', credentials=creds)

        # Call the Tasks API
        results = service.tasklists().list(maxResults=10).execute()
        items = results.get('items', [])
        tasksForListResults = []
        #get the tasks for each task list
        for item in items:
            print(item['title'])
            taskResults = service.tasks().list(tasklist=item['id'], showHidden=True,showDeleted=True).execute()
            taskItems = taskResults.get('items', [])
            tasksForListResults = taskItems
            for taskItem in taskItems:
                print(taskItem['title'])
            print()

        if not items:
            print('No task lists found.')
            return

        print('Task lists:')
        for item in items:
            print(u'{0} ({1})'.format(item['title'], item['id']))
        
        return tasksForListResults
    except HttpError as err:
        print(err)


if __name__ == '__main__':
    tasksForSpecificList = main()
    print(tasksForSpecificList)
    #write the first item in the task list to the serial port
    while True:
        # Read the serial output to see if the pico has given any commands
        # If so, execute them
        if serialCon.in_waiting > 0:
            line = serialCon.readline().decode('utf-8').rstrip()
            if line == 'getTasks':
                #get the tasks for the first task list
                tasks = tasksForSpecificList
                #for each task write it to the serial port
                if tasks:
                    # Wait for a signal from the Pico that it is ready to receive data
                    while True:
                        if serialCon.in_waiting > 0:
                            line = serialCon.readline().decode('utf-8').rstrip()
                            if line == "Ready":
                                break   
                    # Now send the string
                    for task in tasks:
                        serialCon.write((task['title'] + '\n').encode('utf-8'))
                        serialCon.flush()
                        time.sleep(0.1)
                    serialCon.write('end\n'.encode('utf-8'))
                    serialCon.flush()
            else:
                #just ignore the command
                print('Responded with ' + line)