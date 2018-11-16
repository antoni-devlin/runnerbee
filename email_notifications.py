import sendgrid
import os

def sendemail(to, subject, sender, content):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    data = {
      "personalizations": [
        {
          "to": [
            {
              "email": to
            }
          ],
          "subject": subject,
        }
      ],
      "from": {
        "email": sender
      },
      "content": [
        {
          "type": "text/html",
          "value": content
        }
      ]
    }
    response = sg.client.mail.send.post(request_body=data)
    print(response.status_code)
    print(response.body)
    print(response.headers)
    return print('Email sent!')
