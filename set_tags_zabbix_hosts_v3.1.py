#!/usr/bin/python3
#from _typeshed import NoneType
import boto3
from zabbix_api import ZabbixAPI, ZabbixAPIException

#Dictionary Teams
team_list = {'canais': 'channel', 'produtos': 'products', 'plataformas': 'platforms', 'appsclub': 'appsclub', 'bope': 'bope', 'saving': 'saving', 'channel': 'channel', 'platforms': 'platforms', 'product': 'product', 'dataengineer': 'dataengineer', 'infra': 'cloud-eng', 'data-engineering': 'dataengineer', 'cloud-eng': 'cloud-eng', 'operacoes': 'operations', 'operacao': 'operations'}
host_name = ""
tag_update= ""
host_tag = ''
old_tags= {}
targets = {}
host_target = {}
count=0

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


#Get the Host information in the Zabbix-Server
def get_host_target(host, tag):
    try:
        host_name = host
        tag_update = tag
        global hosts_id
        global host_tag
        new = {'tag': 'team', 'value': tag_update}                   
        try:
            hosts = zapi.host.get({
                #"output": "extend",
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
                #host_visiblename = host['name']
                #hos_status = host['status']
                old_tags = host['tags']
                if old_tags:                    
                    for x in old_tags:
                        if new not in old_tags and not (x['tag'] == 'team'):
                            old_tags.append(new)
                            tag_team = zapi.host.update({
                            "hostid": hosts_id,
                            "tags": old_tags
                            })                       
                            print('Tag atualizada com sucesso - {} - {}'.format(host_name, tag_update))
                            return ''
                        elif new in old_tags:
                                for x in old_tags:
                                    if (x['tag'].lower() == 'team'):
                                        host_tag = x['value']                      
                                        if (host_tag == tag_update):                                            
                                            print('Tag ja esta atualizada - {} - {}'.format(host_name, tag_update))
                                            return ''
                        else:
                            print('Nenhuma alteração realizada')
                            return ''                                                                                  
                else:                    
                    old_tags = new
                    tag_team = zapi.host.update({
                            "hostid": hosts_id,
                            "tags": old_tags
                            })
                    print('Tag incluida com sucesso - {} - {}'.format(host_name, tag_update))
                            


                #print('{} - {} - {} - {} - {}'.format(hosts_id, host_name, host_visiblename, hos_status, host_tag))
                    #targets = {'host': host_name, 'team': tag_update }
                #return old_tags
        except ZabbixAPIException as err:
            print('Host não localizado no Zabbix - {}'.format(err))
    except ZabbixAPIException as e:
            print('Host não cadastrado no Zabbix - {}'.format(e))
    

#Updating host by host_tag
def tag_updating(hosts_id, host_tag, tag, old):    
    host_updating = hosts_id
    host_target = host_tag
    tag_update = tag
    olds = old
    if (tag_update != host_target):
        try:            
            new = {'tag': 'team', 'value': tag_update}
            if olds is not None:
                for x in olds:
                    if new not in olds:
                        olds.append(new)
                #print(old_tags)
            else:
                olds = new
            updating = zapi.host.update({
            "hostid": host_updating,
            "tags": olds
            })
            #host_tag = tag_update
            print('Atualização realizada com sucesso no host {}'.format(host_updating))
        except ZabbixAPIException as e:
            print(e)
            
    else:
        print("Tag ja atualizada")


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
        try:
            # This will print will output the value of the Dictionary key 'InstanceId'
            Tags = instance["Tags"]
        except Exception as err:
            print('Erro ao adicionar a lista - {}'.format(err))
        if len(Tags):
            for field in Tags:
                if (field['Key'] == 'opsworks:instance'):
                    #print('{}'.format(field['Key']).lower())
                    zhost = ('{}'.format(field['Value']).lower())
                    host_name = zhost.replace(' ', '')
                    #print(zhost)

                elif (field['Key'] == 'Name'):
                    #print('{}'.format(field['Key']).lower())
                    zhost = ('{}'.format(field['Value']).lower())
                    host_name = zhost.replace(' ', '')
                    #print(zhost)
                    
                if (field['Key'].lower() == 'team'):
                    #print('{}'.format(field['Key']).lower())
                    team = ('{}'.format(field['Value']).lower())
                    try:
                        tag_update=team_list[team]
                    except Exception as err:
                        print('Tag não localizado na lista de times cadastrados - {}'.format(err))
                    #print(tag_update)
            get_host_target(host_name, tag_update)           
            #tag_updating(hosts_id, host_tag, tag_update, olds_tags)                 
        else:
            print('Instancia não possui a chave "Tags"')      
                
zapi.logout()    