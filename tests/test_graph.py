"Test cases for the :module:`arango_orm.database`"

from datetime import date

from arango.exceptions import GraphPropertiesError

from arango_orm.database import Database, Graph, Collection, Relation

from .data import (
    UniversityGraph,
    Student,
    Teacher,
    Subject,
    SpecializesIn,
    Area,
    teachers_data,
    students_data,
    subjects_data,
    specializations_data,
    areas_data,
)


from .fixtures import (  # noqa: F401
    test_db,
    ensure_person_collection,
    ensure_car_collection,
    ensure_student_collection,
    ensure_teacher_collection,
    ensure_subject_collection,
    ensure_area_collection,
    ensure_specializes_in_collection,
    sample_person,
    university_graph,
    university_graph_data,
    university_graph_data_with_relations,
)

from . import all_in


def test_graph_and_collections_exist(test_db: Database, university_graph: Graph):  # noqa: F811
    props = test_db.graph(university_graph.__graph__).properties()

    collection_names = [col["name"] for col in test_db.collections()]
    uni_graph_collections = [
        "studies",
        "specializes_in",
        "teaches",
        "subjects",
        "resides_in",
        "areas",
        "students",
        "teachers",
    ]

    assert university_graph.__graph__ == props["name"]
    assert all_in(uni_graph_collections, collection_names)


def test_data_insertion(university_graph_data):  # noqa: F811
    # If fixture runs without issues then everything is ok.
    assert True


def test_add_relation_using_graph_relation(
    test_db: Database,  # noqa: F811
    university_graph_data_with_relations,  # noqa: F811
):  # noqa: F811
    # If fixture runs without issues then everything is ok.
    assert True


def test_node_expansion_depth_1(
    test_db: Database,  # noqa: F811
    university_graph,  # noqa: F811
    university_graph_data_with_relations,  # noqa: F811
):
    bruce = test_db.query(Teacher).by_key("T001")

    university_graph.expand(bruce, depth=1)

    assert hasattr(bruce, "_relations")
    assert all_in(["resides_in", "specializes_in", "teaches"], bruce._relations)
    assert 1 == len(bruce._relations["resides_in"])
    assert 1 == len(bruce._relations["teaches"])
    assert 3 == len(bruce._relations["specializes_in"])

    # Test for relation's _object_from, _object_to and _next attributes
    assert hasattr(bruce._relations["resides_in"][0], "_object_from")
    assert hasattr(bruce._relations["resides_in"][0], "_object_to")
    assert hasattr(bruce._relations["resides_in"][0], "_next")
    assert bruce._relations["resides_in"][0]._object_from is bruce
    assert "Gotham" == bruce._relations["resides_in"][0]._object_to.key_
    assert "Gotham" == bruce._relations["resides_in"][0]._next.key_
    assert not hasattr(bruce._relations["resides_in"][0]._next, "_relations")


def test_node_expansion_depth_2(
    test_db: Database,  # noqa: F811
    university_graph,  # noqa: F811
    university_graph_data_with_relations,  # noqa: F811
):
    bruce = test_db.query(Teacher).by_key("T001")

    university_graph.expand(bruce, depth=2)

    assert hasattr(bruce, "_relations")
    assert all_in(["resides_in", "specializes_in", "teaches"], bruce._relations)

    assert hasattr(bruce._relations["resides_in"][0]._next, "_relations")
    assert "resides_in" in bruce._relations["resides_in"][0]._next._relations
    assert (
        "John Wayne"
        == bruce._relations["resides_in"][0]._next._relations["resides_in"][0]._next.name
    )
    assert not hasattr(
        bruce._relations["resides_in"][0]._next._relations["resides_in"][0]._next, "_relations"
    )


def test_node_expansion_depth_3(
    test_db: Database,  # noqa: F811
    university_graph,  # noqa: F811
    university_graph_data_with_relations,  # noqa: F811
):
    bruce = test_db.query(Teacher).by_key("T001")

    university_graph.expand(bruce, depth=3)

    assert hasattr(bruce, "_relations")
    assert all_in(["resides_in", "specializes_in", "teaches"], bruce._relations)

    assert hasattr(bruce._relations["resides_in"][0]._next, "_relations")
    assert "resides_in" in bruce._relations["resides_in"][0]._next._relations
    assert (
        "John Wayne"
        == bruce._relations["resides_in"][0]._next._relations["resides_in"][0]._next.name
    )
    assert bruce._relations["teaches"][0]._next._relations["studies"][0]._next._relations[
        "resides_in"
    ][0]._next._key in ["Gotham", "Metropolis", "StarCity"]
    assert hasattr(
        bruce._relations["resides_in"][0]._next._relations["resides_in"][0]._next, "_relations"
    )


def test_inbound_connections_traversal(
    test_db: Database,  # noqa: F811
    university_graph,  # noqa: F811
    university_graph_data_with_relations,  # noqa: F811
):

    gotham = test_db.query(Area).by_key("Gotham")

    university_graph.expand(gotham, depth=1, direction='inbound')

    assert 1 == len(gotham._relations.keys())
    assert 'resides_in' in gotham._relations
    assert 2 == len(gotham._relations['resides_in'])

def test_aql_based_traversal(
    test_db: Database,  # noqa: F811
    university_graph,  # noqa: F811
    university_graph_data_with_relations,  # noqa: F811
):

    obj = university_graph.aql(
        "FOR v, e, p IN 1..2 INBOUND 'areas/Gotham' GRAPH 'university_graph' RETURN p"
    )
    assert isinstance(obj, Area)
    assert 'Gotham' == obj._key
    assert all_in(
        ['Bruce Wayne', 'John Wayne'],
        [r._next.name for r in obj._relations['resides_in']]
    )

def test_aql_based_traversal_with_filter_depth_1(
    test_db: Database,  # noqa: F811
    university_graph,  # noqa: F811
    university_graph_data_with_relations,  # noqa: F811
):

    query = ("FOR v, e, p IN 1..1 ANY 'teachers/T001' GRAPH 'university_graph' "
                "FILTER LIKE(p.edges[0]._id, 'resides_in%') RETURN p")

    obj = university_graph.aql(query)
    assert isinstance(obj, Teacher)
    assert 'Bruce Wayne' == obj.name
    assert 1 == len(obj._relations.keys())
    assert 'resides_in' in obj._relations
    assert 'Gotham' == obj._relations['resides_in'][0]._next._key
    assert not hasattr(obj._relations['resides_in'][0]._next, '_relations')

def test_aql_based_traversal_with_filter_depth_2(
    test_db: Database,  # noqa: F811
    university_graph,  # noqa: F811
    university_graph_data_with_relations,  # noqa: F811
):

    query = ("FOR v, e, p IN 2..2 ANY 'teachers/T001' GRAPH 'university_graph' "
                "FILTER LIKE(p.edges[0]._id, 'resides_in%') RETURN p")

    obj = university_graph.aql(query)
    assert isinstance(obj, Teacher)
    assert 'Bruce Wayne' == obj.name
    assert 1 == len(obj._relations.keys())
    assert 'resides_in' in obj._relations
    assert 'Gotham' == obj._relations['resides_in'][0]._next._key
    assert hasattr(obj._relations['resides_in'][0]._next, '_relations')
    assert 'John Wayne' == \
                obj._relations['resides_in'][0]._next._relations['resides_in'][0]._next.name
    assert not hasattr(obj._relations['resides_in'][0]._next._relations['resides_in'][0]._next,
                        '_relations')
