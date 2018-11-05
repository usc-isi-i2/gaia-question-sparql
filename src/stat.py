
from enum import Enum
from src.utils import write_file, to_string


class Failure(Enum):
    IRRELEVANT = 'irrelevant'
    NO_EP = 'not_find_ep'
    NO_EDGE = 'find_ep_but_not_find_edge'
    NO_JUSTI = 'find_ep_and_edge_but_lack_of_justification'
    ZEROHOP = 'ZEROHOP'


class Stat(object):
    def __init__(self, kb_id):
        self.kb_id = kb_id
        self.success = {}
        self.failed = {
            Failure.IRRELEVANT: [],
            Failure.NO_EP: [],
            Failure.NO_EDGE: [],
            Failure.NO_JUSTI: [],
            Failure.ZEROHOP: []
        }
        self.total_query = 0

    def succeed(self, query_id, find_edge, total_edge):
        self.success[query_id] = '%d / %d' % (find_edge, total_edge)
        self.total_query += 1

    def fail(self, query_id, fail_type, node_uri=()):
        self.failed[fail_type].append('%s : %s' % (query_id, ' '.join(node_uri)))
        self.total_query += 1

    def dumps_json_report(self):
        return to_string({
            'kb_id': self.kb_id,
            'success': self.success,
            'failed': self.failed
        })

    def dump_report(self, output_folder, prefix=''):
        report = '''KB ID: {kb_id}
Total Query: {cnt_query}
Success: {cnt_success}
Failed: {cnt_failed}
    not_find_ep: {cnt_no_ep}
    find_ep_but_not_find_edge: {cnt_no_edge}
    find_ep_and_edge_but_lack_of_justification: {cnt_no_justi}
=NO EDGE LIST=
{no_edge_list}
=NO JUSTI LIST=
{no_justi_list}

        '''.format(kb_id=self.kb_id,
                   cnt_query=str(self.total_query),
                   cnt_success=str(len(self.success)),
                   cnt_failed=str(self.total_query - len(self.success)),
                   cnt_no_ep=str(len(self.failed[Failure.NO_EP])),
                   cnt_no_edge=str(len(self.failed[Failure.NO_EDGE])),
                   cnt_no_justi=str(len(self.failed[Failure.NO_JUSTI])),
                   no_edge_list='\n'.join(self.failed[Failure.NO_EDGE]),
                   no_justi_list='\n'.join(self.failed[Failure.NO_JUSTI])
                   )

        write_file(report, '%s/%s%s_gr_stat.txt' % (output_folder.rstrip('/'), str(prefix), self.kb_id))


class ZHStat(Stat):
    def succeed(self, query_id, find_edge=0, total_edge=0):
        self.success[query_id] = '%d/%d' % (find_edge, total_edge)
        self.total_query += 1

    def fail(self, query_id, fail_type=Failure.ZEROHOP, node_uri=()):
        self.failed[fail_type].append('%s:%s' % (query_id, '|'.join(node_uri)))
        self.total_query += 1

    def dump_report(self, output_folder, prefix=''):
        report = '''KB ID: {kb_id}
Total Query: {cnt_query}
Success: {cnt_success}
Failed: {cnt_failed}
=Failed LIST=
{failed_list}
        '''.format(kb_id=self.kb_id,
                   cnt_query=str(self.total_query),
                   cnt_success=str(len(self.success)),
                   cnt_failed=str(self.total_query - len(self.success)),
                   failed_list='\n'.join(self.failed[Failure.ZEROHOP])
                   )
        write_file(report, '%s/%s%s_zh_stat.txt' % (output_folder.rstrip('/'), str(prefix), self.kb_id))

