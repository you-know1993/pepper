import os
from Queue import Queue

from pepper.framework.config.api import ConfigurationContainer
from pepper.framework.context.api import ContextContainer, Context, ContextWorkerContainer
from pepper.framework.context.worker.context_worker import ContextWorker
from pepper.framework.context.worker.exploration_worker import ExplorationWorker
from pepper.framework.di_container import singleton
from pepper.framework.event.api import EventBusContainer
from pepper.framework.resource.api import ResourceContainer


class DefaultContextContainer(ContextContainer, ConfigurationContainer):
    @property
    @singleton
    def context(self):
        configuration = self.config_manager.get_config("pepper.framework.component.context")
        name = configuration.get("name")
        friends_dir = configuration.get("friends_dir")

        # Initialize the Context for this Application
        friends = [os.path.splitext(path)[0] for path in os.listdir(friends_dir) if path.endswith(".bin")]

        return Context(name, friends)


class DefaultContextWorkerContainer(ContextWorkerContainer, ContextContainer,
                                    EventBusContainer, ResourceContainer, ConfigurationContainer):

    __workers = Queue()

    def start_context_worker(self):
        worker = ContextWorker(self.context, "Context", self.event_bus, self.resource_manager, self.config_manager)
        DefaultContextWorkerContainer.__workers.put(worker)
        worker.start()

    def start_exploration_worker(self):
        worker = ExplorationWorker(self.context, "Exploration", self.event_bus)
        DefaultContextWorkerContainer.__workers.put(worker)
        worker.start()
