'''
This Python Code will generate the respective tables which are stored
into a MySQL database called, 'DATA'. It will automatically retrieve
all the Wemo Switches which have its own respective names. 

The most useful table will be the ones with the switch names. It contains
the information regarding how much current is drained by the appliance,
the total on time, how much time elapses from the ON and OFF state, and the date
and so forth.
'''

# PYMYSQL MODULES
import pymysql
import pymysql.cursors

# OUIMEAUX MODULES
import ouimeaux
from ouimeaux.environment import Environment
from ouimeaux.signals import receiver, statechange, devicefound

# Connect to the database
connection = pymysql.connect(host="localhost",
                            user='root',
                            passwd='ditpwd',
                            db="DATA")

# Initializing the ouimeaux environment
env = Environment()

class TABLE:
    
    def SWITCH(self,list_switches):
        '''This function intakes the list of switches
        and returns the attributes given by the environment
        NOTE: Returns a Tuple
        ''' 
        # Obtaining the switch parameters
        switch_name = list_switches
        switch = env.get_switch(switch_name)
        # Note: Parameters are stored in dictionary
        switch_param = switch.insight_params
        # Delete lastchange: Unnecessary Parameter
        switch_param.pop('lastchange')
        
        return switch_name,switch_param
    
    def COMMANDS(self):
        
        # Commit every data as by default it is False
        connection.autocommit(True)
        
        # Create a cursor object
        cursorObject = connection.cursor()  
            
        for i in range(len(env.list_switches())):
            '''Iterate through all the switches available 
            and create the necessary Tables'''
            
            # Call the helper function SWITCH:
            switch = self.SWITCH(list(env.list_switches())[i])
            sqlCreateTableCommand_temp = str()
            for param in list(switch[1].keys()):
                if param == list(switch[1].keys())[-1]:
                    sqlCreateTableCommand_temp += param + ' int' 
                else:
                    sqlCreateTableCommand_temp += param + ' int' + ', '
        
            # Table commands    
            sqlCreateTableCommand = ("CREATE TABLE " + switch[0] + "("
                                    + sqlCreateTableCommand_temp + ")")
            cursorObject.execute(sqlCreateTableCommand)
            
            # Insert TIME into SWITCH_PARAM table
            sqlInsertColCommand = ('ALTER TABLE ' 
                                + switch[0] + ' ADD TIME TIME FIRST')
            cursorObject.execute(sqlInsertColCommand)
            
            # Insert DATE into SWITCH_PARAM table
            sqlInsertColCommand = ('ALTER TABLE ' 
                                + switch[0] + ' ADD DATE DATE FIRST')
            cursorObject.execute(sqlInsertColCommand)
        
            # Create table DATA
            sqlCreateTableCommand = ("CREATE TABLE "
                                    "DATA_" 
                                    + str(switch[0]) + " (DATE DATE, TIME TIME,"
                                    "STATE varchar(20))")
            cursorObject.execute(sqlCreateTableCommand)
            
            # Create table which stores index values (explained in mysql_plot)
            '''Everytime we re-read the information, we do not want to plot the same
            data we have plotted previously. 
    
            In order to prevent this from happening, we
            create a table and store the previously stored index to MySQL'''
            
            sqlCreateTableCommand = ('CREATE TABLE IND_' 
                                    + switch[0] + ' (DATE DATE, mysql_index int, python_index int)')
            cursorObject.execute(sqlCreateTableCommand)
        
    def CREATE_TABLES(self):
        
        try:
            # Commit every data as by default it is False
            connection.autocommit(True)
            
            # Create a cursor object
            cursorObject = connection.cursor()  
            
            '''ouimeaux notes:
            
            ### useful attributes to SWITCH ###
                [switch].insight_params: This returns
                
                'state': state,
                'lastchange': datetime.fromtimestamp(int(lastchange)), <- popped
                'onfor': int(onfor),
                'ontoday': int(ontoday),
                'ontotal': int(ontotal),
                'todaymw': int(float(todaymw)),
                'totalmw': int(float(totalmw)),
                'currentpower': int(float(currentmw))
                
            ### Turning switch on and off manually ###
                env.get_switch(SWITCH_NAME).on/off()
            '''
            
            env.start()
            env.discover(3)
            switch_temp = list(env.list_switches())
            
            # Table generation not needed if it already exist
            tables = cursorObject.execute('show tables;')
            num_tables = [tables]
            
            if num_tables[0] != 0:
                
                tables = cursorObject.fetchall()
                tables_mysql = [tables_temp[0] for tables_temp in tables]
                for switches in switch_temp:
                    if switches not in tables_mysql == True:
                        self.COMMANDS()
            else:
                self.COMMANDS()
            
        except (KeyboardInterrupt, SystemExit):
            print("Goodbye!")
            sys.exit(0)
        
        except Exception as e:
            print(type(e))
            print("Exeception occured:{}".format(e))
            pass 
        
        finally:
            connection.close()

if __name__ == '__main__':
    
    TABLE = TABLE()
    TABLE.CREATE_TABLES()