from typing import Dict, List

from wat.wat import wat, Trace, EnumeratedTrace
from wat.white_box import Input, RecordId, Rule, WbRecord, WbRelation, WhiteBox

def underline_print(s: str) -> None:
    print(s)
    print('=' * len(s))

def print_provenance(trace: Trace,
                     calculated_provenance: Dict[RecordId, EnumeratedTrace],
                     provenance: List[EnumeratedTrace]) \
                     -> None:
    strings = [f'[{j}] {i}={o}' for j, (i, o) in enumerate(trace)]
    underline_print('Trace')
    print('; '.join(strings))
    print()

    underline_print('Calculated Wat Provenance')
    for rid, t in calculated_provenance.items():
        strings = [f'[{j}] {i}' for j, i, _ in t]
        print(f'{rid.record}')
        print(f'  - {"; ".join(strings)}')
    print()

    underline_print('Wat Provenance')
    for t in provenance:
        strings = [f'[{j}] {i}' for j, i, _ in t]
        print(f'  - {"; ".join(strings)}')
    print()
    print()

class Kvs(WhiteBox):
    def __init__(self) -> None:
        WhiteBox.__init__(self)

        self.create_table('kvs', 2)     # kvs(k, v)
        self.create_table('get_req', 1) # get_req(k)
        self.create_table('set_req', 2) # set_req(k, v)

        kvs = WbRelation('kvs')
        get_req = WbRelation('get_req')
        set_req = WbRelation('set_req')
        self.register_rules('get_req', [
            Rule('get_rep', (kvs * get_req)
                             .select(lambda r: r[0] == r[2])
                             .project([1]))
        ])
        self.register_rules('set_req', [
            Rule('kvs', kvs - (kvs * set_req)
                                .select(lambda r: r[0] == r[2])
                                .project([0, 1])),
            Rule('kvs', kvs + set_req),
            Rule('set_rep', WbRecord(('ok',))),
        ])

class Tours(WhiteBox):
    def __init__(self) -> None:
        WhiteBox.__init__(self)

        self.create_table('Agencies', 3)
        self.create_table('ExternalTours', 4)
        self.create_table('insert_agencies_req', 3)
        self.create_table('insert_external_tours_req', 4)
        self.create_table('query_req', 1)

        Agencies = WbRelation('Agencies')
        ExternalTours = WbRelation('ExternalTours')
        query_req = WbRelation('query_req')
        insert_agencies_req = WbRelation('insert_agencies_req')
        insert_external_tours_req = WbRelation('insert_external_tours_req')

        def f(t):
            a_name, a_based, a_phone, e_name, e_dest, e_type, e_price = t
            return a_name == e_name and e_type == 'boat'
        self.register_rules('query_req', [
            Rule('query_rep',
                 (Agencies * ExternalTours).select(f).project([0, 2]))
        ])
        self.register_rules('insert_agencies_req', [
            Rule('Agencies', Agencies + insert_agencies_req),
            Rule('insert_agencies_rep', WbRecord(('ok', ))),
        ])
        self.register_rules('insert_external_tours_req', [
            Rule('ExternalTours', ExternalTours + insert_external_tours_req),
            Rule('insert_external_tours_rep', WbRecord(('ok', ))),
        ])


def main() -> None:
    kvs = Kvs()
    trace = kvs.run([
        Input('set_req', ('x', '1')),
        Input('set_req', ('x', '2')),
        Input('set_req', ('x', '1')),
        Input('get_req', ('x',)),
    ])
    print_provenance(trace,
                     kvs.get_output_lineage(len(trace) - 1),
                     wat(kvs, trace, len(trace) - 1))

    tours = Tours()
    trace = tours.run([
        Input('insert_agencies_req', ('BayTours',   'San Francisco', '415-1200')),
        Input('insert_agencies_req', ('HarborCruz', 'Santa Cruz',    '831-3000')),
        Input('insert_external_tours_req', ('BayTours',   'San Francisco', 'cable car', '50')),
        Input('insert_external_tours_req', ('BayTours',   'Santa Cruz',    'bus',       '100')),
        Input('insert_external_tours_req', ('BayTours',   'Santa Cruz',    'boat',      '250')),
        Input('insert_external_tours_req', ('BayTours',   'Monterey',      'boat',      '400')),
        Input('insert_external_tours_req', ('HarborCruz', 'Monterey',      'boat',      '200')),
        Input('insert_external_tours_req', ('HarborCruz', 'Carmel',        'train',     '90')),
        Input('query_req', ('',)),
    ])
    print_provenance(trace,
                     tours.get_output_lineage(len(trace) - 1),
                     wat(tours, trace, len(trace) - 1))

if __name__ == '__main__':
    main()
