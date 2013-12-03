__author__ = 'svalleru'
import sys
import json
import smtplib


def get_email_creds():
    with open('gmailAccount.cfg', 'r') as efile:
        creds = [efile.next().strip() for x in xrange(2)]
        email, passwd = creds[0].split('=')[1], creds[1].split('=')[1]
        return email, passwd


def get_sms_params(**params):
    email, passwd = get_email_creds()
    country = params['country']
    carrier = params['carrier']
    text = params['text']
    receiver = params['receiver']
    gateway_addr = None #populated later
    with open('gateways.json', 'r') as gwfile:
        gateways = json.load(gwfile)
    try:
        if country in gateways['countries'].values():
            for isocode, cntry in gateways['countries'].iteritems():
                if str(cntry) == country:
                    break
        else:
            raise ValueError('Country not found!')

        for v in gateways['sms_carriers'][isocode].values():
            if v[0] == carrier:
                gateway_addr = v[1]
                break
        if gateway_addr is None:
                raise ValueError('Carrier not found!')
        return {'gateway_addr': gateway_addr, 'text_body': text, 'email': email, 'passwd': passwd, 'receiver': receiver}
    except ValueError, v:
        print v


def send_sms(param_dict):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(param_dict['email'], param_dict['passwd'])
        server.sendmail(param_dict['email'], str(param_dict['gateway_addr']).replace('{number}', param_dict['receiver'])
            , param_dict['text_body'])
        print 'Message Sent Succesfully!'
    except smtplib.SMTPException, e:
        print e

if __name__ == '__main__':
    try:
        if sys.argv.__len__() != 5:
            raise ValueError('Wrong Argumets!')
        else:
            kwargs = dict(x.split('=', 1) for x in sys.argv[1:])
            send_sms(get_sms_params(**kwargs))
    except ValueError, e:
        print '''===USAGE===\npython pyText.py country='United States' carrier='AT&T Wireless' receiver='4088675309' text='Good Bye Cruel World!'
              '''