from .export import Connections
from .model_util import instance2names


class Links:
    def __init__(self,instance):
        self.instance = instance
        self.connections = Connections(instance)

    def collect_relation_instances(self):
        self.relation_instances = []
        for instance in self.connections.instances:
            app_name, model_name = instance2names(instance)
            if 'relation' in model_name.lower():
                self.relation_instances.append(instance)

    @property
    def n_connections(self):
        if not hasattr(self,'relation_instances'):
            self.collect_relation_instances()
        n = len(self.relation_instances)
        if self.instance._meta.model_name == 'publication':
            n += len(self.instance.publisher.all())
        return n

    def get_plots(self):
        self._plots, self.no_plots, self.error = [], [], []
        for instance in self.connections.instances:
            if instance != self.instance:
                if hasattr(instance,'set_other'):
                    instance.set_other(self.instance)
                try:self._plots.append(instance.plot())
                except: 
                    self.no_plots.append(instance)
                    self.error.append(instance)
            else: self.no_plots.append(instance)

    def get_pop_ups(self):
        self.pop_ups, self.no_pop_ups = [], []
        for instance in self.connections.instances:
            if instance != self.instance and hasattr(instance,'pop_up'):
                if hasattr(instance,'set_other'): 
                    self.pop_ups.append(instance.pop_up(self.instance))
                else: self.pop_ups.append(instance.pop_up())
            else:self.no_pop_ups.append(instance)
    
    @property
    def plots(self):
        if not hasattr(self,'_plots'): self.get_plots()
        return self._plots

            

