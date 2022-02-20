import math

from mesa import Agent, Model
from transitions import Machine, State

class MarketPlaceAgent(Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model,x,y):
        super().__init__(unique_id, model)
        # 0 fossile #1 wind #2 nuclear #3 solar
        self.Umarket=[]
        self.inbox={}
        self.inboxit={}
        self.prices_request=[]
        self.x=x
        self.y=y
        self.purchasehistory= {}
        self.energyselled = []
        self.lastpurchaseday=[0 for i in range(24)]
        self.purchaseday=[0 for i in range(24)]
        self.energy_day = [0, 0, 0, 0]
        for i in range(4):
            self.energyselled.append([])
        for i in range(24):
            self.purchasehistory[i]=[]

    def setup(self):
        for i in self.model.schedule.agents:
            self.inbox[i.get_id()]=[]
            self.inboxit[i.get_id()]=0
        self.get_producers()

        #self.purchaseday=[0 for i in range(24)]
        self.price_sent={}
        for p in self.producers:
            self.price_sent[p]=0
        self.market =[]



    def get_producers(self):
        """
        Method to add variable 'producers' that contains all the producers
        
        Returns
        -------
        None.
        """
        self.producers=[]
        for j in self.model.schedule.agents:
            if(j.get_id() != self.unique_id):
                if(j.is_producer):
                    self.producers.append(j.get_id())


    def received_all_prices(self):
        """
        Verify if all prices have be sent

        Returns
        -------
        bool
        """
        for i in self.price_sent.keys():
            if(self.price_sent[i]==0):
                return False
        return True

    def save_purchase(self, purchase):
        for j in range(len(purchase)):
            for i in range(24):
                nb = 0
                for a in purchase[j]:
                    #print("a: ", a[0], a[1], self.market[a[1]], self.market[a[1]][2])
                    if (i == a[0]):
                        self.energy_day[self.market[a[1]][2]] += 1
                        nb += 1
                self.purchaseday[i] += nb


    def atomic_response(self,sender_id,message):
        """
        Give a response (to) sender given his message

        Parameters
        ----------
        sender_id : int
            identification number of the sender
        message : list
            first element is the type of message
            second element is purhcase wanted
        Returns
        -------
        str
            ok_prices - the sender is a producer and has sent his prices
            ok_purchase - the sender is a consumer and has bought energy from someone
        str, market
            prices - gives the current market prices (sender is a consumer)

        """
        if(message[0] == "prices"):
            for j in message[1]:
                self.market.append((sender_id,j[0],j[1]))
            self.price_sent[sender_id]=1
            return ("ok_prices",None)
        if(message[0]== "ask_prices"):
            if(self.received_all_prices()):
                return ("prices",self.market)
            else:
                return ("no_prices_yet",None)
        if(message[0]=="purchase"):
            self.save_purchase(message[1])
            return ("ok_purchase",None)
        return None





    def response_step(self):
        for i in self.inbox.keys():
            if(self.inboxit[i]<len(self.inbox[i])):
                self.model.send(self.unique_id,i,self.atomic_response(i,self.inbox[i][self.inboxit[i]]))
                self.inboxit[i]+=1



    def get_id(self):
        """
        Gives the marketplace id

        Returns
        -------
        TYPE
            DESCRIPTION.
        """
        return self.unique_id

    def step(self):
        """
        Prints the 

        Returns
        -------
        None.
        """
        #print(str(self.unique_id) + ": InboxID:" + str(self.inboxit) + ": Inbox :" + str(self.inbox))
        #for j in self.market:
        #    print("is: " + str(j))
        self.response_step()
        #print("purchaseday!", self.purchaseday)

    def reset_day(self):
        self.lastpurchaseday=self.purchaseday.copy()
        self.purchaseday = [0 for i in range(24)]
        for i in range(4):
            self.energyselled[i].append(self.energy_day[i])
        for i in range(len(self.purchaseday)):
            self.purchasehistory[i].append(self.purchaseday[i])
        self.setup()



