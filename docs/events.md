# Events

The ORM supports data life-cycle events for running code before or after a data modification operation (add/update/delete). Apart from these there is support for creating custom events though in this case the user/developer is responsible for trigerring the events.

## Built-in events

There are 6 built-in events that are trigerred automatically and any callback function registered/listening for these gets called. These are:

- `pre_add` called before inserting an entity into the database.
- `post_add` called after inserting an entity into the database.
- `pre_update` called before updating an entity in the database.
- `pre_update` called after updating an entity in the database.
- `pre_delete` called before removing an entity from the database.
- `pre_delete` called after removing an entity from the database.


## Using events

To use any event you need to register your callback code (usually a function) against the event. This can be done in two ways. Either using the [listen][arango_orm.event.listen] function or the [listens_for][arango_orm.event.listens_for] decorator.

```python
from arango import ArangoClient
from arango_orm import Collection, Database
from arango_orm.event import listen, listens_for


client = ArangoClient(hosts='http://localhost:8529')
db = Database(client.db('test', username='test', password='test'))


class Person(Collection):
    __collection__ = 'people'

    name: str


def before_add_callback(target: Person, event: str, db: Database):
    print(f"About to insert Person {target.name} into the db.")


listen(Person, 'pre_add', before_add_callback)

@listens_for(
    Collection,
    ['pre_add', 'post_add', 'pre_update', 'post_update', 'pre_delete', 'post_delete']
)
def db_audit(target: Collection, event:str, *args, **kwargs):
    db = kwargs['db']
    print(f"{event} on {target} for {db}")


db.create_collection(Person)
db.add(Person(name='abc'))
```

output:

```
About to insert Person abc into the db.
pre_add on Person(key_=None rev_=None name='abc') for <StandardDatabase test>
post_add on Person(key_='12644011' rev_=None name='abc') for <StandardDatabase test>
Out[1]: {'_id': 'people/12644011', '_key': '12644011', '_rev': '_gtrY3JK---'}
```


## Custom Events

In addition to the built-in events you can create custom events and have code registered against them. However you are responsible for dispatching these event too.


```python

from arango_orm import Collection
from arango_orm.event import listen, listens_for, dispatch


class Process(Collection):
    __collection__ = 'processes'

    pid: int
    cmd: str

    def sleep(self):
        # actual sleep logic
        dispatch(self, "gone_to_sleep")


@listens_for(Process, 'gone_to_sleep')
def monitor_sleep(target: Process, event: str, *args, **kwargs):
    print(f"Process {target.pid} has gone to sleep")

p1 = Process(pid=10, cmd='ls')
p1.sleep()

# output
Process 10 has gone to sleep
```
