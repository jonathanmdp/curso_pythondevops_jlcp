#!/usr/bin/python3
import boto3
from zabbix_api import ZabbixAPI, ZabbixAPIException

#Dictionary Teams
team_list = {'canais': 'channel', 'produtos': 'product', 'plataformas': 'platforms', 'appsclub': 'appsclub', 'bope': 'bope', 'saving': 'saving', 'channel': 'channel', 'platforms': 'platforms', 'product': 'product', 'dataengineer': 'dataengineer', 'infra': 'cloud-eng', 'data-engineering': 'dataengineer', 'cloud-eng': 'cloud-eng', 'operacoes': 'operations', 'operacao': 'operations'}
#host_name = ""
#tag_update= ""
#host_tag = ''


# The hostname at which the Zabbix web interface is available
ZABBIX_SERVER = 'http://192.168.1.103/zabbix'
zapi = ZabbixAPI(ZABBIX_SERVER, timeout=180)
try:
    # Login to the Zabbix API
    zapi.login('Admin', 'zabbix')
    print('Conectado na API do Zabbix {}'.format(zapi.api_version()))
except Exception as err:
    print('Falha ao conectar na API do Zabbix: {}'.format(err))


#session profile for aws
mysession = boto3.session.Session(profile_name='default')
ec2client = boto3.client('ec2')
ec2filter = [{}]

#request instance
response = ec2client.describe_instances(
    Filters = [{
        'Name': 'instance-state-name',
        'Values': ['running']
        }]
)
for reservation in response["Reservations"]:
    for instance in reservation["Instances"]:
        #This sample print will output entire Dictionary object
        #print(instance)
        try:
            # This will print will output the value of the Dictionary key 'InstanceId'
            Tags = instance["Tags"]
        except Exception as err:
            print('Erro ao adicionar a lista - {}'.format(err))

        if Tags:
            for field in Tags:
                if (field['Key'] == 'opsworks:instance'):
                    #print('{}'.format(field['Key']).lower())
                    zhost = ('{}'.format(field['Value']).lower())
                    try:
                        host_name = zhost
                    except Exception as err:
                        print('Nao encontrado - {}'.format(err))
                    
                    print('host - {}'.format(zhost))

                if (field['Key'].lower() == 'team'):
                    #print('{}'.format(field['Key']).lower())
                    team = ('{}'.format(field['Value']).lower())
                    try:
                        tag_update=team_list[team]
                        print('team - {}'.format(tag_update))
                    except Exception as err:
                        print('Não encontrado na lista - {}'.format(err))
         
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
                            old_tags = host['tags']
                            new = {'tag': 'team', 'value': tag_update}
                            for x in old_tags:
                                if new not in old_tags:
                                    old_tags.append(new)
                            tag_team = zapi.host.update({
                            "hostid": host_update,
                            "tags": old_tags
                            })
                            host_tag = tag_update

                print('{} - {} - {} - {} - {}'.format(hosts_id, host_name, host_visiblename, hos_status, host_tag))
            except ZabbixAPIException as e:
                print(e)


            # Update host_tag
            if host_tag == None:
                try:
                    old_tags = host['tags']
                    new = {'tag': 'team', 'value': tag_update}
                    for x in old_tags:
                        if new not in old_tags:
                            old_tags.append(new)
                    #print(type(old_tags))
                    updating = zapi.host.update({
                    "hostid": host_update,
                    "tags": old_tags
                    })
                    host_tag = tag_update
                    print("Atualização realizada com sucesso")
                except ZabbixAPIException as e:
                    print(e)

            else:
                print("Tag ja atualizada")
        else:
            print('Instancia sem chave "Tags"')

