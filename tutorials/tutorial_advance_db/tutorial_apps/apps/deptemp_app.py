from confapp import conf
from pyforms_web.widgets.django import ModelAdminWidget

from tutorial.models import DeptEmp

class DeptEmpAdminApp(ModelAdminWidget):
    

    UID   = 'tutorial-DeptEmp-app'.lower()
    MODEL = DeptEmp
    
    TITLE = 'Dept Emps'

    #list of filters fields
    #LIST_FILTER    = ['emp_no','dept_no','from_date','to_date']

    #list of fields to display in the table
    #LIST_DISPLAY   = ['emp_no','dept_no','from_date','to_date']
    
    #fields to be used in the search
    #SEARCH_FIELDS  = ['emp_no','dept_no','from_date','to_date']
    
    #sub models to show in the interface
    #INLINES        = []
    
    #formset of the edit form
    #FIELDSETS      = ['emp_no','dept_no','from_date','to_date']
    
    #read only fields
    #READ_ONLY      = ['emp_no','dept_no','from_date','to_date']
    
    #EDITFORM_CLASS = DeptEmpModelFormWidget    #edit form class
    #CONTROL_LIST   = ControlQueryList #Control to be used in to list the values
    
    #AUTHORIZED_GROUPS   = ['superuser'] #groups with authorization to visualize the app
    
    ########################################################
    #### ORQUESTRA CONFIGURATION ###########################
    ########################################################
    LAYOUT_POSITION      = conf.ORQUESTRA_HOME
    ORQUESTRA_MENU       = 'left>DepartmentsAdminApp'
    ORQUESTRA_MENU_ORDER = 0
    ORQUESTRA_MENU_ICON  = 'dollar'
    ########################################################
    
    
    