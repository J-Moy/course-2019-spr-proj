import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd


class interesting_spaces(dml.Algorithm):
    contributor = 'zui_sarms'
    reads = ['zui_sarms.landmarks', 'zui_sarms.parks']
    writes = ['zui_sarms.interesting_spaces']

    @staticmethod
    def execute(trial=False):
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('zui_sarms', 'zui_sarms')

        parks = repo['zui_sarms.parks']
        landmarks = repo['zui_sarms.landmarks']

        df_parks = pd.DataFrame(list(parks.find()))

        df_landmarks = pd.DataFrame(list(landmarks.find()))

        df_landmarks = df_landmarks.rename(index=str, columns={'Name_of_Pr': 'Name',
                                                               'Neighborho': 'Neighborhood'})
        df_landmarks['Type'] = 'Landmark'

        df_parks = df_parks.rename(index=str, columns={'SITE_NAME': 'Name',
                                                       'DISTRICT': 'Neighborhood',
                                                       'ADDRESS': 'Address',
                                                       'TypeLong': 'Type'})

        df2_parks = df_parks[['Name', 'Neighborhood', 'Address', 'Type']]
        df2_landmarks = df_landmarks[['Name', 'Neighborhood', 'Address', 'Type']]

        frames = [df2_parks, df2_landmarks]
        final_df = pd.concat(frames)

        print(list(final_df))

        repo.dropCollection("interesting_spaces")
        repo.createCollection("interesting_spaces")
        repo['zui_sarms.interesting_spaces'].insert_many(final_df.to_dict(orient='records'))
        repo['zui_sarms.interesting_spaces'].metadata({'complete': True})
        print(repo['zui_sarms.interesting_spaces'].metadata())

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}

    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):

        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:zui_sarms#interesting_spaces', {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        landmarks = doc.entity('dat:zui_sarms#landmarks',{'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'json'})
        parks = doc.entity('dat:zui_sarms#parks',{'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'json'})
        merge = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(merge, this_script)
        doc.usage(merge, parks, startTime, None, {prov.model.PROV_TYPE: 'ont:Retrieval'})
        doc.usage(merge, landmarks, startTime, None, {prov.model.PROV_TYPE: 'ont:Retrieval'})

        interesting_spaces = doc.entity('dat:zui_sarms#interesting_spaces', {prov.model.PROV_LABEL: 'Interesting Spaces', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(interesting_spaces, this_script)
        doc.wasGeneratedBy(interesting_spaces, merge, endTime)
        doc.wasDerivedFrom(interesting_spaces, landmarks, merge, merge, merge)
        doc.wasDerivedFrom(interesting_spaces, parks, merge, merge, merge)

        return doc
