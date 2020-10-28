
import boto3
import json

from zabbix_api import ZabbixAPI, ZabbixAPIException

#Dictionary Teams
team_list = {'canais': 'channel', 'produtos': 'product', 'plataformas': 'platforms'}
host_name = ""
tag_update= ""


#session profile for aws
mysession = boto3.session.Session(profile_name='default')
ec2client = boto3.client('ec2')

#request instance
response = ec2client.describe_instances()
for reservation in response["Reservations"]:
    for instance in reservation["Instances"]:
        #This sample print will output entire Dictionary object
        print(instance)
        # This will print will output the value of the Dictionary key 'InstanceId'
        Tags = instance["Tags"]
        for field in Tags:
            if (field['Key'] == 'opsworks:instance'):
                #print('{}'.format(field['Key']).lower())
                zhost = ('{}'.format(field['Value']).lower())
                host_name = zhost
                print(zhost)

            if (field['Key'].lower() == 'team'):
                #print('{}'.format(field['Key']).lower())
                team = ('{}'.format(field['Value']).lower())
                tag_update=team_list[team]
                print(tag_update)

# The hostname at which the Zabbix web interface is available
ZABBIX_SERVER = 'http://192.168.1.103/zabbix'
zapi = ZabbixAPI(ZABBIX_SERVER, timeout=180)


try:

    # Login to the Zabbix API
    zapi.login('Admin', 'zabbix')
    print('Conectado na API do Zabbix {}'.format(zapi.api_version()))

except Exception as err:
    print('Falha ao conectar na API do Zabbix: {}'.format(err))

#Get the Host information in the Zabbix-Server
try:

    hosts = zapi.host.get({
        "output": "extend",
        "filter": {
            "host": [
                host_name
            ]
        },
        "selectTags": [
            "tag", "value"]
    })
    for host in hosts:
        hosts_id = host['hostid']
        host_name = host['host']
        host_update = hosts_id
        host_visiblename = host['name']
        hos_status = host['status']
        for xtag in host['tags']:
            if (xtag['tag'].lower() == 'team'):
                host_tag = xtag['value']
            else:
                teste = host['tags']
                novo = {'tag': 'team', 'value': tag_update}
                teste.append(novo)
                print(type(teste))
                teg_team = zapi.host.update({
                "hostid": host_update,
                "tags": [
                        {
                         teste
                        }
                    ]
                })
                host_tag = tag_update

        print('{} - {} - {} - {} - {}'.format(hosts_id, host_name, host_visiblename, hos_status, host_tag))
except ZabbixAPIException as e:
    print(e)


# Update host_tag
if (host_tag!=tag_update):
    try:
        teste = host['tags']
        novo = {'tag': 'team', 'value': tag_update}
        teste.append(novo)
        updating = zapi.host.update({
            "hostid": host_update,
            "tags": [
                    {
                        teste
                    }
                ]
        })
        print("Atualização realizada com sucesso")
    except ZabbixAPIException as e:
        print(e)
        sys.exit()
else:
    print("Tag ja atualizada")
