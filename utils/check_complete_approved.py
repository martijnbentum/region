from utils import model_util as mu

def count_instances(instances):
    return len(instances)

def count_complete_instances(instances): 
    return len([x for x in instances if x.complete])

def count_approved_instances(instances): 
    return len([x for x in instances if x.approved])


def counts_for_instances(instances = None):
    if not instances: instances.mu.get_all_instances()
    n_instances = count_instances(instances)
    n_complete= count_complete_instances(instances)
    n_approved= count_approved_instances(instances)
    print('number of items in database:',n_instances)
    print('number of items complete:',n_complete)
    print('number of items approved:',n_approved)


def counts_per_category(instances = None):
    if not instances: instances.mu.get_all_instances()
    d = make_category_dict(instances)
    for name, instances in d.items():
        print('Counts for items of type:',name)
        counts_for_instances(instances)
        print('---')

def make_category_dict(instances = None):
    if not instances: instances.mu.get_all_instances()
    d = {}
    for instance in instances:
        name = instance._meta.model_name
        if name not in d.keys(): d[name] = []
        d[name].append(instance)
    return d

