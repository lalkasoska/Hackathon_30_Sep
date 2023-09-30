# Django
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from .utils import get_time_from_a_to_b

# local Django

from .models import Order

def welcome(request):
    """
    Renders the welcome page.
    """
    return render(request, 'registration/login.html')


@login_required
def home(request):
    """
    Renders the home page with the user's memories.
    """
    user = request.user
    orders = Order.objects.filter(user=user)


    context = {
        'user': user,
        'orders': orders,
    }
    return render(request, 'home.html', context)







def build_routes(request):
    """Solve the VRP with time windows."""
    print("BUILDING ROUTES!!!")
    # Instantiate the data problem.
    orders = Order.objects.all()
    data = {}
    data["time_matrix"] = [[get_time_from_a_to_b(order.ord_adress_loc, order2.ord_adress_loc) for order2 in orders] for order in orders]
    data["time_windows"] = []
    for order in orders:
        t = order.ord_time
        seconds = t.hour*3600 + t.minute*60 + t.second
        data["time_windows"].append((seconds//60-60, seconds//60+60))
    data["num_vehicles"] = 4
    data["depot"] = 0
    print(data)
    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data["time_matrix"]), data["num_vehicles"], data["depot"]
    )

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def time_callback(from_index, to_index):
        """Returns the travel time between the two nodes."""
        # Convert from routing variable Index to time matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["time_matrix"][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(time_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Time Windows constraint.
    time = "Time"
    routing.AddDimension(
        transit_callback_index,
        1800,  # allow waiting time
        1800,  # maximum time per vehicle
        False,  # Don't force start cumul to zero.
        time,
    )
    time_dimension = routing.GetDimensionOrDie(time)
    # Add time window constraints for each location except depot.
    for location_idx, time_window in enumerate(data["time_windows"]):
        if location_idx == data["depot"]:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
    # Add time window constraints for each vehicle start node.
    depot_idx = data["depot"]
    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(
            data["time_windows"][depot_idx][0], data["time_windows"][depot_idx][1]
        )

    # Instantiate route start and end times to produce feasible times.
    for i in range(data["num_vehicles"]):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i))
        )
        routing.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(routing.End(i)))

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    def print_solution(data, manager, routing, solution):
        """Prints solution on console."""
        print(f"Objective: {solution.ObjectiveValue()}")
        time_dimension = routing.GetDimensionOrDie("Time")
        total_time = 0
        for vehicle_id in range(data["num_vehicles"]):
            index = routing.Start(vehicle_id)
            plan_output = f"Route for vehicle {vehicle_id}:\n"
            while not routing.IsEnd(index):
                time_var = time_dimension.CumulVar(index)
                plan_output += (
                    f"{manager.IndexToNode(index)}"
                    f" Time({solution.Min(time_var)},{solution.Max(time_var)})"
                    " -> "
                )
                index = solution.Value(routing.NextVar(index))
            time_var = time_dimension.CumulVar(index)
            plan_output += (
                f"{manager.IndexToNode(index)}"
                f" Time({solution.Min(time_var)},{solution.Max(time_var)})\n"
            )
            plan_output += f"Time of the route: {solution.Min(time_var)}min\n"
            print(plan_output)
            total_time += solution.Min(time_var)
        print(f"Total time of all routes: {total_time}min")
    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)
    return render(request, 'home.html')

if __name__ == "__main__":
    build_routes()