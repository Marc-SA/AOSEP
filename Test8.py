from Environnement import Environnement
from MarketPlaceAgent import MarketPlaceAgent
from ProsumerAgent import *


""" Testing if incrementing seasons works
"""

fridge= [[[1 for i in range(24)] ,24]]*7

washingMachine = [[[1 for i in range(24)],2],
                    [[1 for i in range(24)],0],
                    [[1 for i in range(24)],0],
                    [[1 for i in range(24)],0],
                    [[1 for i in range(24)],0],
                    [[1 for i in range(24)],0],
                    [[1 for i in range(24)],0]]

TV = [[[1 for i in range(24)] ,4]]*5
TV.append([[0 for i in range(24)] ,0])
TV.append([[0 for i in range(24)] ,0])

jobs = [fridge]
Sjobs = [washingMachine,TV]

mdl = Environnement();
mrkt= MarketPlaceAgent(5,mdl,8,8)

# Producer Agent : fossil and solar
ag1 = ProsumerAgent(1,[1,0,0,1],False,mdl,1,1)
# Consumer Agent prefers green > renewable > prices
ag2 = ProsumerAgent(2,[0,0,0,0],True,mdl,2,2,jobs=jobs,Sjobs=Sjobs,weights=[0.2,0.3,0.5])

lagents= [ag1,ag2]

mdl.setup(lagents,mrkt,10,10,15)
mrkt.setup()
ag1.setup()
ag2.setup()
mdl.rweek()
agent_counter = len(lagents)+2
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def get_data():
    grid = []
    for cell in mdl.grid:
        if cell == []:
            grid.append(None)
        elif isinstance(cell[0], ProsumerAgent):
            grid.append(cell[0].get_dict())
        elif isinstance(cell[0], MarketPlaceAgent):
            grid.append(18)
    return {
        "grid": grid,
        "width": mdl.grid.width, "height": mdl.grid.height}

@app.route("/req", methods=["POST"])
def req():
    if request.args.get("action") == "run_day":
        mdl.rday()
    elif request.args.get("action") == "delete":
        x = int(request.args.get("x"))
        y = int(request.args.get("y"))
        l = list(mdl.grid)[y*mdl.grid.width+x]
        if len(l) > 0 and not isinstance(l[0], MarketPlaceAgent):
            mdl.delete_agent(l[0])
    elif request.args.get("action") == "add":
            x = int(request.args.get("x"))
            y = int(request.args.get("y"))
            global agent_counter
            ag = ProsumerAgent(agent_counter,
                model=mdl,
                x=y,
                y=x,
                is_cons=eval(json.loads(request.data)["is_cons"]),
                producer_table=eval(json.loads(request.data)["producer_table"]),
                jobs=eval(json.loads(request.data)["jobs"]),
                Sjobs=eval(json.loads(request.data)["Sjobs"]),
                weights=eval(json.loads(request.data)["weights"]),
                table_wind=eval(json.loads(request.data)["table_wind"]),
                nuclear_price=eval(json.loads(request.data)["nuclear_price"]),
                solar_price=eval(json.loads(request.data)["solar_price"]),
                fossileprice=eval(json.loads(request.data)["fossileprice"]),
                treshold=eval(json.loads(request.data)["treshold"]),
                )
            agent_counter += 1
            mdl.add_agent(ag)
    return jsonify({"data": get_data(), "chart_data": [mrkt.energyselled, mrkt.lastpurchaseday]})

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=8080)