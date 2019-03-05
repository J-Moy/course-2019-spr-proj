import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd


class masterList(dml.Algorithm):
    contributor = 'ashwini_gdukuray_justini_utdesai'
    reads = ['ashwini_gdukuray_justini_utdesai.massHousing', 'ashwini_gdukuray_justini_utdesai.secretary'] # is going to have to read in the master list from mongodb
    writes = ['ashwini_gdukuray_justini_utdesai.masterList'] # will write a dataset that is companies in top 25 that are also certified MBE

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ashwini_gdukuray_justini_utdesai', 'ashwini_gdukuray_justini_utdesai')

        # Need to standardize the columns and field structure of massHousing and secretary and union the two
        # in order to create a master MBE list, and then store it in the DB

        massHousing = repo['ashwini_gdukuray_justini_utdesai.massHousing']
        secretary = repo['ashwini_gdukuray_justini_utdesai.secretary']

        massHousingDF = pd.DataFrame(list(massHousing.find()))
        secretaryDF = pd.DataFrame(list(secretary.find()))

        print(massHousingDF)
        print(secretaryDF['MBE - Y/N'])

        # convert zip codes to strings and 5 digits long
        secretaryDF['Zip'] = secretaryDF['Zip'].astype('str')
        secretaryDF['Zip'] = secretaryDF['Zip'].apply(lambda zipCode: ((5 - len(zipCode))*'0' + zipCode \
                                                        if len(zipCode) < 5 else zipCode)[:5])
        secretaryDF = secretaryDF.loc[secretaryDF['MBE - Y/N'] == 'Y']
        secretaryDF = secretaryDF[['Business Name', 'Address', 'City', 'Zip', 'State', 'Description of Services', 'MBE - Y/N']]

        print(secretaryDF)
        # list of column names underneath
        #print(list(massHousingDF))
        #print(list(secretaryDF))

        repo.dropCollection("masterList")
        repo.createCollection("masterList")
        #repo['ashwini_gdukuray_justini_utdesai.masterList'].insert_many(records)
        #repo['ashwini_gdukuray_justini_utdesai.masterList'].metadata({'complete': True})
        #print(repo['ashwini_gdukuray_justini_utdesai.masterList'].metadata())

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}

    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        pass
        """
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('alice_bob', 'alice_bob')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:alice_bob#example',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:wc8w-nujj',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        get_found = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_lost = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_found, this_script)
        doc.wasAssociatedWith(get_lost, this_script)
        doc.usage(get_found, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=Animal+Found&$select=type,latitude,longitude,OPEN_DT'
                   }
                  )
        doc.usage(get_lost, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=Animal+Lost&$select=type,latitude,longitude,OPEN_DT'
                   }
                  )

        lost = doc.entity('dat:alice_bob#lost',
                          {prov.model.PROV_LABEL: 'Animals Lost', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(lost, this_script)
        doc.wasGeneratedBy(lost, get_lost, endTime)
        doc.wasDerivedFrom(lost, resource, get_lost, get_lost, get_lost)

        found = doc.entity('dat:alice_bob#found',
                           {prov.model.PROV_LABEL: 'Animals Found', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(found, this_script)
        doc.wasGeneratedBy(found, get_found, endTime)
        doc.wasDerivedFrom(found, resource, get_found, get_found, get_found)

        repo.logout()

        return doc
        """


'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
example.execute()
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof
