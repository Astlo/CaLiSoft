from neomodel import StructuredNode, ArrayProperty, StringProperty, RelationshipFrom, RelationshipTo
from neomodel import db


# DAO. Objects used to access data in neo4j database
class LicenseModel(StructuredNode):
    labels = ArrayProperty()
    permissions = ArrayProperty(index=True)
    obligations = ArrayProperty(index=True)
    prohibitions = ArrayProperty(index=True)
    hashed_sets = StringProperty(unique_index=True)

    followings = RelationshipTo("LicenseModel", "Compatible")
    precedings = RelationshipFrom("LicenseModel", "Compatible")
    datasets = RelationshipTo("DatasetModel", "Protects")


def license_filter_labels(label):
    results, columns = db.cypher_query("match(license:LicenseModel) WHERE any(label in license.labels WHERE label CONTAINS '{}') RETURN license".format(label))
    return [LicenseModel().inflate(row[0]) for row in results]


def license_filter_sets(values, set_name):
    results, columns = db.cypher_query("match(license:LicenseModel) WHERE all(value IN {values} WHERE value IN license.{set_name}) RETURN license"
                                       .format(values=values, set_name=set_name))
    return [LicenseModel().inflate(row[0]) for row in results]


def get_leaf_licenses():
    results, columns = db.cypher_query("match(license:LicenseModel) WHERE not ()-[:Compatible]->(license) RETURN license")
    return [LicenseModel().inflate(row[0]) for row in results]


def get_compatible_licenses(hashed_sets):
    results, columns = db.cypher_query("match(license:LicenseModel {{hashed_sets:'{}'}})-[:Compatible *0..]->(comp_license:LicenseModel) RETURN distinct comp_license".format(hashed_sets))
    return [LicenseModel().inflate(row[0]) for row in results]


def get_compliant_licenses(hashed_sets):
    results, columns = db.cypher_query("match(license:LicenseModel {{hashed_sets:'{}'}})<-[:Compatible *0..]-(comp_license:LicenseModel) RETURN distinct comp_license".format(hashed_sets))
    return [LicenseModel().inflate(row[0]) for row in results]


class DatasetModel(StructuredNode):
    label = StringProperty(index=True)
    description = StringProperty()
    uri = StringProperty(unique_index=True)
    hashed_uri = StringProperty(unique_index=True)

    license = RelationshipFrom("LicenseModel", "Protects")


def dataset_filter_search(query):
    results, columns = db.cypher_query("match(dataset:DatasetModel) WHERE dataset.label CONTAINS '{query}' OR dataset.description CONTAINS '{query}' OR dataset.uri CONTAINS '{query}' RETURN dataset"
                                       .format(query=query))
    return [DatasetModel().inflate(row[0]) for row in results]
