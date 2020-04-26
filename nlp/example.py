from operator import attrgetter

import datetime  # for analytics only
import matplotlib.pyplot as plt  # for plotting


class DAG:

    def __init__(self, path, show_analytics, optimize=True):

        ######## ANALYTICS #########
        z = datetime.datetime.now()
        ############################

        (num_stations, max_arrival_time, dep_nodes) = self.__read_data_to_nodes(path)

        ############# ANALYTICS ############
        old_num_cons = len(dep_nodes)      #
        x = datetime.datetime.now()        #
        prep_time = (x - z).total_seconds()
        ####################################

        if not len(dep_nodes):  # fail safe if no connections
            if show_analytics:
                self.print_analytics(prep_time, 0, 0, 0, 0)
            return

        if optimize:
            dep_nodes = self.__clean_nodes(
                num_stations, max_arrival_time, dep_nodes)

        dep_nodes = self.__fuze_duplicate_deps(dep_nodes)

        ######### ANALYTICS ##########
        opt_node_num = len(dep_nodes)
        ##############################

        self.nodes = self.__get_all_nodes(dep_nodes)

        ############# ANALYTICS #############
        a = datetime.datetime.now()         #
        layer_time = (a - x).total_seconds()
        #####################################

        self.__add_waiting_edges(self.nodes)

        ############# ANALYTICS ##############
        b = datetime.datetime.now()          #
        weight_time = (b - a).total_seconds()
        ######################################

        self.__calculate_max_probs()
        self.max_prob = self.__retrieve_max_prob()

        ############# ANALYTICS #################
        c = datetime.datetime.now()             #
        calc_time = (c - b).total_seconds()     #
        total_alg_time = (c - x).total_seconds()
        #########################################

        print("optimized:", optimize, "by percentage:", round(
            100 * (1 - opt_node_num / old_num_cons), 2), "%")

        if show_analytics:
            self.print_analytics(prep_time, layer_time,
                                 weight_time, calc_time, total_alg_time)

    def print_analytics(self, prep_time, layer_time, weight_time, calc_time, total_alg_time):
        print()
        print("##################ANALYTICS####################")
        print("prep time was:", prep_time, "seconds")
        print("layer time was:", layer_time, "seconds")
        print("weight time was:", weight_time, "seconds")
        print("calc time was:", calc_time, "seconds")
        print("total algorithm took:", total_alg_time, "seconds")
        print("------------------------------------------------")
        print("max probability is:", self.max_prob * 100, "%")
        print("###############################################")

    def __read_data_to_nodes(self, path):
        data = open(path, "r")
        num_busses_and_stations = data.readline()
        num_busses_and_stations_seperated = num_busses_and_stations.split()
        num_busses = int(num_busses_and_stations_seperated[0])
        num_stations = int(num_busses_and_stations_seperated[1])
        max_arrival_time = int(data.readline())
        print("number of connections: ", num_busses)

        dep_nodes = []

        for _ in range(num_busses):
            line_data = data.readline().split()
            start_station = int(line_data[0])
            end_station = int(line_data[1])
            dep_time = int(line_data[2])
            arr_time = int(line_data[3])
            prob = float(line_data[4])
            if (dep_time > max_arrival_time or arr_time > max_arrival_time or start_station == 1):
                continue
            arr_node = Node(None, end_station, arr_time)
            dep_node = Node(Edge(arr_node, prob), start_station, dep_time)

            dep_nodes.append(dep_node)

        return (num_stations, max_arrival_time, dep_nodes)

    def __calculate_max_probs(self):
        self.nodes.sort(key=attrgetter("time"))
        for node in reversed(self.nodes):
            node.update_max_prob()

    def __add_waiting_edges(self, nodes):
        nodes.sort(key=attrgetter("station", "time"))
        next_dep = (-1, None)
        for i in range(0, len(nodes) - 1):
            from_node = nodes[i]
            if i < next_dep[0]:
                from_node.waiting_edge = Edge(next_dep[1], 0)
                continue
            for j in range(i + 1, len(nodes)):
                to_node = nodes[j]
                if from_node.station == 1 or to_node.station != from_node.station:
                    break
                if not to_node.connection_edges:
                    continue
                next_dep = (j, to_node)
                from_node.waiting_edge = Edge(to_node, 0)
                break

    def __fuze_duplicate_deps(self, dep_nodes):
        dep_nodes.sort(key=attrgetter("time", "station"))
        cur_dep = dep_nodes[0]
        deps_to_fuze = []
        fuzed_dep_nodes = []

        for node in dep_nodes:
            if cur_dep.station != node.station or node.time != cur_dep.time:
                dep_node = self.__fuze_dep_nodes(deps_to_fuze)
                fuzed_dep_nodes.append(dep_node)
                deps_to_fuze = [node]
                cur_dep = node
            else:
                deps_to_fuze.append(node)

        fuzed_dep_nodes.append(self.__fuze_dep_nodes(
            deps_to_fuze))  # fuze the remaining

        return fuzed_dep_nodes

    def __fuze_dep_nodes(self, nodes):
        fuzed_node = nodes[0]
        for i in range(1, len(nodes)):
            fuzed_node.connection_edges.append(nodes[i].connection_edges[0])
        return fuzed_node

    def __clean_nodes(self, num_stations, max_arrival_time, dep_nodes):
        dep_nodes.sort(key=attrgetter("time"))
        reachable_table = [(False, max_arrival_time)
                           for i in range(num_stations)]
        reachable_table[0] = (True, -1)
        reachable_nodes = [Node(None, 0, -1)]  # TODO: Not nice

        for node in dep_nodes:
            if reachable_table[node.station][0] and reachable_table[node.station][1] < node.time:
                to_node = node.connection_edges[0].pointer
                new_time = min(
                    to_node.time, reachable_table[to_node.station][1])
                reachable_table[to_node.station] = (True, new_time)
                reachable_nodes.append(node)

        return reachable_nodes

    def __get_all_nodes(self, dep_nodes):
        nodes = dep_nodes
        for node in dep_nodes:
            for edge in node.connection_edges:
                nodes.append(edge.pointer)

        return nodes

    def __retrieve_max_prob(self):
        return self.nodes[0].max_prob


class Node:
    def __init__(self, connection_edge, station, time):
        self.connection_edges = []
        if connection_edge:
            self.connection_edges.append(connection_edge)
        self.waiting_edge = None
        self.station = station
        self.time = time
        self.max_prob: float = 0

        # ONLY FOR PLOTTING
        self.position = Position(0, 0)

    def __get_edge_counter_prob(self, edge):
        if edge is not None:
            return 1 - edge.prob
        return 1

    def update_max_prob(self):
        if self.station == 1:
            self.max_prob = 1
            return

        alter_prob = self.waiting_edge.pointer.max_prob if self.waiting_edge else 0

        max_probs = [alter_prob]
        for edge in self.connection_edges:
            con_prob = edge.pointer.max_prob * edge.prob
            wait_prob = alter_prob * self.__get_edge_counter_prob(edge)
            max_probs.append(con_prob + wait_prob)

        self.max_prob = max(max_probs)


class Edge:
    def __init__(self, pointer, prob):
        self.pointer = pointer
        self.prob = prob

    def __str__(self):
        return " max_prob: " + str(self.pointer.max_prob) + " prob: " + str(self.prob)

    def __repr__(self):
        return self.__str__()


#################### PLOTTING THINGS ONLY ########################

class Position:  # class for plotting
    def __init__(self, x, y):
        self.x = x
        self.y = y


FACE_COLOR = "white"  # "#F4F3F5"
AXIS_COLOR = "black"  # "#9A9A9A"
NODE_AND_EDGE_COLOR = "black"  # "C97679"
AIRPORT_COLOR = "black"  # "#76CBB7"
WAITING_EDGE_COLOR = "gray"  # "#9A9A9A"
PROB_TEXT_COLOR = "black"  # "#7E7B7B"
PROB_BG_COLOR = "white"  # "#E2E2E2"
NODE_TEXT_COLOR = "black"


def set_up_plot(fig):

    fig.patch.set_facecolor(FACE_COLOR)
    plt.rcParams["font.family"] = "monospace"
    plt.rcParams["font.monospace"] = "Menlo"
    plt.subplots_adjust(top=1, bottom=0, right=0.98)

    ax = fig.add_subplot(111)
    ax.spines["bottom"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_color(AXIS_COLOR)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="y", colors=AXIS_COLOR)


def finish_plot_setup(positions_in_plot):

    plt.ylabel("time", fontdict=dict(color=AXIS_COLOR))

    plt.gca().invert_yaxis()
    plt.gca().invert_xaxis()
    plt.gca().axes.get_xaxis().set_visible(False)
    plt.gca().set_facecolor(FACE_COLOR)


def plot_connections_and_save_positions(positions_in_plot, nodes, max_probs):
    # plot all the connections
    for node in nodes:
        if node.connection_edges:  # if we have a connection
            y_pos = node.time
            x_pos = get_plot_x_pos(y_pos, positions_in_plot)
            positions_in_plot.append(Position(x_pos, y_pos))
            node.position = Position(x_pos, y_pos)

            for i in range(len(node.connection_edges)):
                pos = Position(
                    x_pos + i, node.connection_edges[i].pointer.time)
                positions_in_plot.append(pos)
                node.connection_edges[i].pointer.position = pos

                # plot connection probs
                vec = Position((node.position.x - pos.x) * 0.5,
                               (node.position.y - pos.y) * 0.5)
                # plt.text(pos.x + vec.x, pos.y + vec.y,
                #          str(int(node.connection_edges[i].prob * 100)) + "%",
                #          horizontalalignment="center", weight="bold", verticalalignment="center",
                #          fontsize=12, color=PROB_TEXT_COLOR, zorder=15,
                #          bbox=dict(facecolor=PROB_BG_COLOR, boxstyle="round", edgecolor=PROB_BG_COLOR))
                plt.plot([node.position.x, pos.x], [node.position.y,
                                                    pos.y], linewidth=2, color=NODE_AND_EDGE_COLOR)


def plot_nodes_and_waiting_edges(nodes, max_probs):
    # plot  all the waiting edges
    for node in nodes:
        dest_color = AIRPORT_COLOR if node.station == 1 else NODE_AND_EDGE_COLOR
        if max_probs:
            # plot max probs in stead of nodes
            plt.text(node.position.x, node.position.y, str(int(node.max_prob * 100)) + "%",
                     color=NODE_TEXT_COLOR, horizontalalignment="center", weight="bold", verticalalignment="center", fontsize=12, zorder=15,
                     bbox=dict(facecolor=FACE_COLOR, boxstyle="round", edgecolor=dest_color))
        else:
            plt.text(node.position.x, node.position.y, node.station, horizontalalignment="center",
                     weight="bold", verticalalignment="center", fontsize=12, color=NODE_TEXT_COLOR, zorder=15)
            plt.plot(node.position.x, node.position.y, "o", ms=20,
                     markerfacecolor=FACE_COLOR, markeredgecolor=dest_color, markeredgewidth=1.5, color=dest_color, zorder=10)
        if node.waiting_edge:
            plt.plot([node.position.x, node.waiting_edge.pointer.position.x], [
                     node.position.y, node.waiting_edge.pointer.position.y], linewidth=2, linestyle="--", color=WAITING_EDGE_COLOR, zorder=5)


def plot_DAG(dag, max_probs=False, fig_num=1):
    nodes = dag.nodes
    fig = plt.figure(fig_num, figsize=(6, 8), facecolor=FACE_COLOR)

    master_node = nodes[0]
    master_node.position = Position(0, -1)

    positions_in_plot = [master_node.position]  # position for master node

    set_up_plot(fig)

    plot_connections_and_save_positions(positions_in_plot, nodes, max_probs)
    plot_nodes_and_waiting_edges(nodes, max_probs)

    finish_plot_setup(positions_in_plot)


def get_plot_x_pos(time, nodes_pos):
    x = 0
    while any((pos.x == x and pos.y >= time) for pos in nodes_pos):
        x += 1
    return x


if __name__ == "__main__":
    dag = DAG("/Users/daniel/Desktop/Uni/5. Semester/Proseminar/data/easy.txt",
              show_analytics=True, optimize=True)
    plot_DAG(dag, max_probs=False)
    plt.show()
