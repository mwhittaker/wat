from typing import List

from wat import *

def print_provenance(trace: Trace, provenance: List[EnumeratedTrace]) -> None:
    strings = [f'[{j}] {i}={o}' for j, (i, o) in enumerate(trace)]
    print('; '.join(strings))

    for t in provenance:
        strings = [f'[{j}] {i}' for j, i, _ in t]
        print(f'  - {"; ".join(strings)}')
    print()
def main():
    k = Kvs()
    b = Bexpr()
    l = Lists()
    db = Db()

    trace = k.run([k.set('x', 1), k.set('x', 2), k.get('x')])
    print_provenance(trace, wat(k, trace, len(trace) - 1))

    trace = k.run([k.set('x', 1), k.set('x', 2), k.set('x', 1), k.get('x')])
    print_provenance(trace, wat(k, trace, len(trace) - 1))

    trace = k.run([k.set('x', 1), k.set('x', 1), k.get('x')])
    print_provenance(trace, wat(k, trace, len(trace) - 1))

    trace = k.run([k.set('x', 0), k.add('x', 1), k.add('x', -1), k.get('x')])
    print_provenance(trace, wat(k, trace, len(trace) - 1))

    av = Var('a')
    bv = Var('b')
    cv = Var('c')
    dv = Var('d')
    e = Or([And([av, dv]), And([bv, cv])])
    trace = b.run([b.set('a'), b.set('b'), b.set('c'), b.set('d'), b.eval(e)])
    print_provenance(trace, wat(b, trace, len(trace) - 1))

    trace = l.run([
        l.rpush('b'),
        l.rpush('c'),
        l.rpush('d'),
        l.lpush('a'),
        l.remove('c'),
        l.rpop(),
        l.lpop(),
        l.index(0),
    ])
    print_provenance(trace, wat(l, trace, len(trace) - 1))

    e = Or([And([Not(bv), av, cv]), dv])
    trace = b.run([b.set('a'), b.set('b'), b.set('c'), b.set('d'), b.eval(e)])
    print_provenance(trace, wat(b, trace, len(trace) - 1))

    e = And([av, Or([cv, dv])])
    trace = b.run([b.set('a'), b.set('b'), b.set('c'), b.set('d'), b.eval(e)])
    print_provenance(trace, wat(b, trace, len(trace) - 1))

    q = DbDiff(DbRelation('R'), DbRelation('S'))
    trace = db.run([
        db.create('R', 1),
        db.create('S', 1),
        db.insert('R', ['a']),
        db.insert('R', ['b']),
        db.insert('S', ['b']),
        db.query(q),
    ])
    print_provenance(trace, wat(db, trace, len(trace) - 1))

    q = DbCup(DbRelation('R'), DbDiff(DbRelation('S'), DbRelation('T')))
    trace = db.run([
        db.create('R', 1),
        db.create('S', 1),
        db.create('T', 1),
        db.insert('R', ['a']),
        db.insert('S', ['a']),
        db.insert('T', ['a']),
        db.query(q),
    ])
    print_provenance(trace, wat(db, trace, len(trace) - 1))

    def leq3(t):
        x, = t
        return int(x) <= 3
    q = DbSelect(DbDiff(DbRelation('R'), DbRelation('S')), leq3)
    trace = db.run([
        db.create('R', 1),
        db.create('S', 1),
        db.insert('R', ['1']),
        db.insert('R', ['3']),
        db.insert('R', ['4']),
        db.insert('R', ['6']),
        db.insert('S', ['2']),
        db.insert('S', ['3']),
        db.insert('S', ['5']),
        db.insert('S', ['6']),
        db.query(q),
    ])
    print_provenance(trace, wat(db, trace, len(trace) - 1))

    # See page 383 of "Provenance in Databases: Why, How, and Where".
    def f(t):
        a_name, a_based, a_phone, e_name, e_dest, e_type, e_price = t
        return a_name == e_name and e_type == 'boat'
    Agencies = DbRelation('Agencies')
    ExternalTours = DbRelation('ExternalTours')
    q = DbProject(DbSelect(DbCross(Agencies, ExternalTours), f), [0, 2])
    trace = db.run([
        db.create('Agencies', 3),
        db.create('ExternalTours', 4),
        db.insert('Agencies', ['BayTours',   'San Francisco', '415-1200']),
        db.insert('Agencies', ['HarborCruz', 'Santa Cruz',    '831-3000']),
        db.insert('ExternalTours', ['BayTours',   'San Francisco', 'cable car', '50']),
        db.insert('ExternalTours', ['BayTours',   'Santa Cruz',    'bus',       '100']),
        db.insert('ExternalTours', ['BayTours',   'Santa Cruz',    'boat',      '250']),
        db.insert('ExternalTours', ['BayTours',   'Monterey',      'boat',      '400']),
        db.insert('ExternalTours', ['HarborCruz', 'Monterey',      'boat',      '200']),
        db.insert('ExternalTours', ['HarborCruz', 'Carmel',        'train',     '90']),
        db.query(q),
    ])
    print_provenance(trace, wat(db, trace, len(trace) - 1))

if __name__ == '__main__':
    main()
