#!/usr/bin/env python

'''
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     Aug 2014
@author:    Priyanka/Maria
@summary:   As a LITP User, I want a model extension for system parameters,
            so that I can include them in my deployment description and
            I want to ensure platform configures system parameters based on
            node definitions, so that kernel parameters can be adjusted when
            needed.
            Agile: STORY LITPCDS-2327 and LITPCDS-5774
'''

from redhat_cmd_utils import RHCmdUtils
from litp_generic_test import GenericTest, attr
import test_constants
import os


class Story2327Story5774(GenericTest):

    '''
    As a LITP User, I want a model extension for system parameters,
    so that I can include them in my deployment description and
    I want to ensure platform configures system parameters based on
    node definitions, so that kernel parameters can be adjusted when needed.
    '''

    def setUp(self):
        """
        Description:
            Runs before every single test
        Actions:
            1. Call the super class setup method
            2. Set up variables used in the tests
        Results:
            The super class prints out diagnostics and variables
            common to all tests are available.
        """
        # 1. Call super class setup
        super(Story2327Story5774, self).setUp()
        self.test_ms = self.get_management_node_filename()
        self.test_nodes = self.get_managed_node_filenames()
        self.redhatutils = RHCmdUtils()

    def tearDown(self):
        """
        Description:
            Runs after every single test
        Actions:
            1. Perform Test Cleanup
        Results:
            Items used in the test are cleaned up and the
            super class prints out end test diagnostics
        """
        super(Story2327Story5774, self).tearDown()

    def _create_sysparam_config(self, config_path, config_name):
        """
        Description:
            Creates sysparam node config
        Args:
            config_path(str): config_path
            config_name(str): config_name
        Actions:
            1. Create sysparam config
        Results:
            system-param config item-type is successfully created
        """
        config_type = "sysparam-node-config"
        # Create a sysparam-node-config
        config_url = config_path + "/{0}".format(config_name)
        self.execute_cli_create_cmd(
            self.test_ms, config_url, config_type)
        return config_url

    def _create_system_param(self, param_path, system_param_name, props):
        """
        Description:
            Create a system-param item-type
        Args:
            param_path (str): sysparam path
            system_param_name (str): system-param name
            props (str): properties to be created

        Actions:
            1. Create system-param item-type
        Results:
            system-param item-type is successfully created
        """

        sys_param_path = param_path + "/params/{0}".format(system_param_name)
        self.execute_cli_create_cmd(
            self.test_ms, sys_param_path, "sysparam", props)
        return sys_param_path

    def _update_system_param_props(self, param_path, system_param_name, props):
        """
        Description:
            Updates a system-param item-type
        Args:
            param_path (str): system-param path
            system_param_name (str): system-param name
            props (str): properties to be updated
        Actions:
            1. Update system-param item-type
        Results:
            system-param item-type is successfully updated
        """
        sys_param_path = param_path + "/params/{0}".format(system_param_name)
        self.execute_cli_update_cmd(
            self.test_ms, sys_param_path, props)

    def _update_keyvalue_in_sysctl_conf(self, node, old_value, new_value):
        """
        Description:
            Function that replaces the key=old_value in sysctl.conf file with
            key=new_value and loads the /etc/sysctl.conf settings
        Args:
            node (str) : The node to find the file on.
           old_value (str): The old string that should be replaced.
           new_value (str): The new string.
       Actions:
            1. Replace the old value of system parameter with new value
        Results:
             Successfully replaced the value

        """

        # Replace the existing value with new value
        cmd = self.redhatutils.get_replace_str_in_file_cmd(
            old_value, new_value, test_constants.SYSCTL_CONFIG_FILE,
            sed_args='-i')
        std_out, std_err, rc = self.run_command(node, cmd, su_root=True)
        self.assertEquals([], std_err)
        self.assertEqual([], std_out)
        self.assertEquals(0, rc)

        # Load the sysctl.conf file
        cmd = self.redhatutils.get_sysctl_cmd(
            '-e -p {0}'.format(test_constants.SYSCTL_CONFIG_FILE))
        stdout, stderr, rc = self.run_command(node, cmd, su_root=True)
        self.assertEquals([], stderr)
        self.assertNotEqual([], stdout)
        self.assertEquals(0, rc)

    def _find_keyvalue_in_sysctl_conf(self, node, option, positive=True):
        """
        Description:
            Function to find a specific key = value
            in the sysctl.conf file.
        Args:
            node (str) : The node to find the file on.
            option (str): parameter name
        Actions:
            1. finds the key in the file
        Results:
             Successfully checked the parameter and returns key=value

        """
        cmd = self.redhatutils.get_grep_file_cmd(
            test_constants.SYSCTL_CONFIG_FILE, option)
        std_out, std_err, rc = self.run_command(node, cmd, su_root=True)
        if positive is True:
            self.assertEquals([], std_err)
            self.assertNotEqual([], std_out)
            self.assertEquals(0, rc)
            return std_out[0]
        else:
            self.assertEquals([], std_err)
            self.assertEquals([], std_out)
            self.assertEquals(1, rc)

    def _find_values_sysctl(self, node, option):
        """
        Description:
            Function to find a specific key = value
            in the sysctl
        Args:
            node (str) : The node to find the file on.
            option (str): parameter name
        Actions:
            1. finds the key in the file
        Results:
             Successfully checked the parameter and returns key=value

        """
        # Find key values in sysctl.conf file
        cmd = "/sbin/sysctl '{0}'".format(option)
        stdout, stderr, rc = self.run_command(node, cmd, su_root=True)
        self.assertEquals([], stderr)
        self.assertFalse([], stdout)
        self.assertEquals(0, rc)
        return stdout[0]

    def _check_memory_values(self, node, option):
        """
        Description:
            Function to find a specific key = value
            in the memory.
        Args:
            node (str) : The node to find the file on.
            option (str): parameter name
        Actions:
            1. finds the key in the memory
        Results:
             Successfully checked the parameter and returns key=value

        """
        cmd = self.redhatutils.get_sysctl_cmd(
            '{0}'.format(option))
        stdout, stderr, rc = self.run_command(node, cmd, su_root=True)
        self.assertEquals([], stderr)
        self.assertNotEqual([], stdout)
        self.assertEquals(0, rc)
        return stdout[0]

    def _assert_err_msg_list(self, err_list, results):
        """
        Description:
            Function that checks that each error message in a list, of size
        n,is associated with a unique path which precedes the error message
        in the list of error messages generated
        Args:
            err_list (list): list of error messages and paths
            results (dict):  dictionary of error data
        """
        # Validate error message path
        index = results['index']
        if results['path'] == None:
            msg_index = index
        else:
            msg_index = index + 1

        if results['path'] != None:
            self.assertEqual(
                err_list[index], results['path'],
                'Expected path "{0}", found "{1}"'
                .format(results['path'], err_list[index]))

        # Validate error message
        self.assertEqual(
            err_list[msg_index], results['msg'],
            'Expected msg "{0}", found "{1}"'
            .format(results['msg'], err_list[msg_index]))

    @attr('all', 'revert', 'story2327_5774', 'story2327_5774_tc01',
          'cdb_priority1')
    def test_01_p_create_remove_system_param_positive(self):
        """
        @tms_id: litpcds_2327_5774_tc01
        @tms_requirements_id: LITPCDS-2327, LITPCDS-5774
        @tms_title: Create and remove a system param with existing sysparams
        @tms_description: Test that a preexisting key & a key not present in
            sysctl.conf file can be configured and removed through the
            deployment model and that a manually updated key will not be
            overwritten
        @tms_test_steps:
            @step: Find a sysparam-node-config on node1
            @result: sysparam-node-config is found on node1
            @step: Check file for the preexisting key(a) and find its value
            @result: Key is found with a value
            @step: Create system-param on node1 with preexisting key(a)
            @result: Preexisting system-param is create with new value in litp
            @step: Find sysparam-node-config on node2
            @result: sysparam-node-config is found on node2
            @step: Check file for the preexisting key(b) and find its value
            @result: Key is found with a value
            @step: Create another system-param on node2 with key(b) in the file
            @result: Preexisting system-param is create with new value in litp
            @step: Update another preexisting key(c) in the file manually
            @result: Preexisting system-param is updated
            @step: Create plan, Run plan
            @result: litp plan runs successfully
            @step:Check sysctl.conf file on node1 contains updated sysparm
            @result: node1 contains updated sysparm
            @step: Check the value is not updated on node2 config file
            @result: Node2 sysparm not updated with new value
            @step: Check sysctl.conf file contains key(b) on node2
            @result: sysctl.conf file contains key(b) on node2
            @step: Check the value is not updated on node1 config file
            @result: sysparm not updated on node1 config file
            @step: Check that puppet has not overridden the updated value
                    for key(c) in the sysctl.conf file
            @result: Puppet has not overridden the updated value for key(c)
            @step: Manually update the key (a) in the sysctl.conf file on node1
            @result: Key (a) updated in the sysctl.conf file on node1
            @step: Check that when the value of a param under puppet control
                    is changed, it is reverted
            @result: value of a param under puppet control gets reverted
            @step: Remove the system-param item-types that have been created
            @result: item and for "ForRemoval"
            @step: Create plan, Run plan
            @result: system-param keys, (a),(b) and (c) has removed from
                sysctl.conf file
            @step: Return key (c) to it's original value
            @result: Key (c) to it's original value
            @step: Check the keys, (a),(b) and (c) is not removed from memory
            @result: Keys, (a),(b) and (c) are not removed from the memory
        @tms_test_precondition:NA
        @tms_execution_type: Automated
        """

        # Find the desired collection on nodes
        nodes_path = self.find(self.test_ms, "/deployments", "node", True)
        self.assertTrue(
            len(nodes_path) > 1,
            "The LITP Tree has less than 2 nodes defined")
        node1_path = nodes_path[0]
        node2_path = nodes_path[1]
        test_node1 = self.get_node_filename_from_url(self.test_ms, node1_path)
        test_node2 = self.get_node_filename_from_url(self.test_ms, node2_path)

        # Create sysctl keys required for test
        sysctl_key1 = "fs.suid_dumpable"
        sysctl_key2 = "kernel.core_pattern"
        sysctl_key3 = "kernel.core_uses_pid"

        # Create sysctl values required for test
        sysctl_value1 = "1"
        sysctl_value2 = "/var/coredumps/core.%h.%e.pid%p.usr%u.sig%s.tim%t"
        sysctl_value3 = "22"

        # copy sysctl.conf file to tmp_location
        local_config_filepath = test_constants.SYSCTL_CONFIG_FILE
        config_filepath = "/tmp/sysctl"
        self.assertTrue(self.cp_file_on_node(
            test_node1, local_config_filepath, config_filepath,
            su_root=True))
        self.assertTrue(self.cp_file_on_node(
            test_node2, local_config_filepath, config_filepath,
            su_root=True))

        try:
            self.log('info', '1. Find the sysparam-node-config'
                             ' already on node1')
            sysparam_node1_config = self.find(
                self.test_ms, "/deployments", "sysparam-node-config")[0]

            self.log('info', '2. Check file for the preexisting'
                             ' key(a) on both nodes and find its value')
            node1_key1_val = self._find_keyvalue_in_sysctl_conf(
                test_node1, sysctl_key1)
            node2_key1_val = self._find_keyvalue_in_sysctl_conf(
                test_node2, sysctl_key1)

            # check to ensure that the value returned is not equal to
            # the value you intend to set.
            check_value_is_valid = sysctl_key1 + " = " + sysctl_value1
            self.assertNotEqual(node1_key1_val, check_value_is_valid)

            self.log('info', '3. Create system-param on '
                             'node1 with preexisting key(a) '
                             'in the file')
            props = 'key="{0}" value="{1}"'.format(sysctl_key1, sysctl_value1)
            system_param1 = self._create_system_param(
                sysparam_node1_config, "sysctltest01a", props)

            self.log('info', '4. Find the sysparam-node-config '
                             'already on node2')
            sysparam_node2_config = self.find(
                self.test_ms, "/deployments", "sysparam-node-config")[1]

            self.log('info', '5.  Check file for the '
                             'preexisting key(b) on both '
                             'nodes and find its value')
            node2_key2_val = self._find_keyvalue_in_sysctl_conf(
                test_node2, sysctl_key2)
            node1_key2_val = self._find_keyvalue_in_sysctl_conf(
                test_node1, sysctl_key2)

            # check to ensure that the value returned is not equal to
            # the value you intend to set.
            check_value_created = sysctl_key2 + " = " + sysctl_value2
            self.assertNotEqual(node2_key2_val, check_value_created)

            self.log('info', '6. Create another '
                             'system-param with key(b) in the file  '
                             'on node2')
            props = ('key="{0}" value="{1}"'.format(sysctl_key2,
                                                    sysctl_value2))
            system_param2 = self._create_system_param(
                sysparam_node2_config, "sysctltest01b", props)

            # Find pre-existing key(c) in sysctl.conf file on node1
            orig_key3_val = self._find_keyvalue_in_sysctl_conf(
                test_node1, sysctl_key3)

            self.log('info', '7. Update another '
                             'pre-existing key(c) in the file manually')
            updated_key3_val = "{0} = '{1}'".format(sysctl_key3, sysctl_value3)
            self._update_keyvalue_in_sysctl_conf(
                test_node1, orig_key3_val, updated_key3_val)

            self.log('info', '8. Create plan')
            self.execute_cli_createplan_cmd(self.test_ms)

            self.log('info', '9. Run plan')
            self.execute_cli_runplan_cmd(self.test_ms)

            # Wait for plan to complete
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_COMPLETE))

            self.log('info', '10. Check sysctl.conf file '
                             'contains updated preexisting key(a)'
                             'to the value on node1')
            updated_key1_val = self._find_keyvalue_in_sysctl_conf(
                test_node1, sysctl_key1)
            self.assertNotEqual(node1_key1_val, updated_key1_val)

            self.log('info', '11.  Check the value is '
                             'not updated on node2 config file')
            get_key1_val = self._find_keyvalue_in_sysctl_conf(
                test_node2, sysctl_key1)
            self.assertEqual(node2_key1_val, get_key1_val)

            self.log('info', '12. Check sysctl.conf '
                             'file contains updated key(b) '
                             'to the value on node2')
            updated_key2_val = self._find_keyvalue_in_sysctl_conf(
                test_node2, sysctl_key2)
            self.assertNotEqual(updated_key2_val, node2_key2_val)

            self.log('info', '13.  Check the value is '
                             'not updated on node1 config file')
            get_key2_val = self._find_keyvalue_in_sysctl_conf(
                test_node1, sysctl_key2)
            self.assertEqual(node1_key2_val, get_key2_val)

            self.log('info', '14. Check that puppet '
                             'has not overridden the updated '
                             'value for key(c) in the sysctl.conf file')
            self.assertEqual(self._find_keyvalue_in_sysctl_conf(
                test_node1, sysctl_key3), updated_key3_val.replace("'", ""))

            self.log('info', '15. Manually update the key '
                             '(a) in the sysctl.conf file')
            manual_update_key1_val = "{0} = '5535'".format(
                sysctl_key1)
            self._update_keyvalue_in_sysctl_conf(
                test_node1, updated_key1_val, manual_update_key1_val)

            self.log('info', '16. Check that when the '
                             'value of a param under puppet '
                             'control is reverte')
            cmd_to_run = \
                "/bin/cat {0} | /bin/grep '{1} = {2}'".format(
                    test_constants.SYSCTL_CONFIG_FILE, sysctl_key1,
                    sysctl_value1)
            self.assertTrue(self.wait_for_puppet_action(
                self.test_ms, test_node1, cmd_to_run, 0, su_root=True))

            self.log('info', '17. Remove the system-param'
                             ' item-types that have been created '
                             'and remove manually updated key(c)')
            self.execute_cli_remove_cmd(self.test_ms, system_param1)
            self.execute_cli_remove_cmd(self.test_ms, system_param2)
            remove_key3_manualy = " "
            self._update_keyvalue_in_sysctl_conf(
                test_node1, updated_key3_val, remove_key3_manualy)

            self.log('info', '18. Check their states are, "ForRemoval"')
            state_value = self.execute_show_data_cmd(
                self.test_ms, system_param1, "state")
            self.assertEqual(state_value, "ForRemoval")

            state_value = self.execute_show_data_cmd(
                self.test_ms, system_param2, "state")
            self.assertEqual(state_value, "ForRemoval")

            self.log('info', '19. Create plan')
            self.execute_cli_createplan_cmd(self.test_ms)

            self.log('info', '22. Run plan')
            self.execute_cli_runplan_cmd(self.test_ms)

            self.log('info', 'Wait for plan to complete')
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_COMPLETE,
                seconds_increment=0.5))

            self.log('info', '23.Check the keys, (a),(b) and (c) has '
                             'removed from sysctl.conf file')
            cmd_to_run = self.redhatutils.get_grep_file_cmd(
                test_constants.SYSCTL_CONFIG_FILE, sysctl_key1)
            self.assertTrue(self.wait_for_puppet_action(
               self.test_ms, test_node1, cmd_to_run, 1))

            # self._find_keyvalue_in_sysctl_conf(
            #    test_node1, sysctl_key1, positive=False)
            self._find_keyvalue_in_sysctl_conf(
                test_node2, sysctl_key2, positive=False)
            self._find_keyvalue_in_sysctl_conf(
                test_node1, sysctl_key3, positive=False)

            self.log('info', '24.Check the keys, '
                             '(a) and (c) is not removed from memory')
            self._check_memory_values(test_node1, sysctl_key1)
            self._check_memory_values(test_node2, sysctl_key2)
            self._check_memory_values(test_node1, sysctl_key3)

        finally:

            # copy  back sysctl.conf
            local_config_filepath = test_constants.SYSCTL_CONFIG_FILE
            config_filepath = "/tmp/sysctl"
            self.assertTrue(self.cp_file_on_node(
                test_node1, config_filepath, local_config_filepath,
                su_root=True))

            self.assertTrue(self.cp_file_on_node(
                test_node2, config_filepath, local_config_filepath,
                su_root=True))

            # Load the sysctl.conf file on node1
            cmd = self.redhatutils.get_sysctl_cmd(
                '-e -p {0}'.format(test_constants.SYSCTL_CONFIG_FILE))
            stdout, stderr, rc = self.run_command(test_node1,
                                                  cmd, su_root=True)
            self.assertEquals([], stderr)
            self.assertNotEqual([], stdout)
            self.assertEquals(0, rc)

            # Load the sysctl.conf file on node2
            cmd = self.redhatutils.get_sysctl_cmd(
                '-e -p {0}'.format(test_constants.SYSCTL_CONFIG_FILE))
            stdout, stderr, rc = self.run_command(test_node2,
                                                  cmd, su_root=True)
            self.assertEquals([], stderr)
            self.assertNotEqual([], stdout)
            self.assertEquals(0, rc)

    @attr('all', 'revert', 'story2327_5774', 'story2327_5774_tc02')
    def test_02_n_check_system_parameter_validation_negative(self):
        """
        @tms_id: litpcds_2327_5774_tc02
        @tms_requirements_id: LITPCDS-2327, LITPCDS-5774
        @tms_title: Check validation error on system param
        @tms_description: Test the system-param item-type validation
        @tms_test_steps:
            @step: Create a sysparam-node-config
            @result: sysparam-node-config is created in litp model
            @step: Attempt to create system-param key with an empty string
            @result: Correct ValidationError is returned
            @step: Attempt to create system-param with key contains ,
            @result: Correct ValidationError is returned
            @step: Attempt to create system-param with key contains =
            @result: Correct ValidationError is returned
            @step: Attempt to create system-param value to empty string
            @result: Correct ValidationError is returned
            @step: Attempt to create system-param with an additional property
            @result: Correct ValidationError is returned
            @step: Attempt to create system-param with a missing value property
            @result: Correct ValidationError is returned
            @step: Attempt to create system-param with missing key property
            @result: Correct ValidationError is returned
            @step: Check the same key cannot be specified more than once
            @result: fails with error at create_plan
            @step: Attempt to remove the key
            @result: Correct ValidationError is returned
            @step: Attempt to remove the value
            @result: Correct ValidationError is returned
            @step: Attempt to remove non existing system-param
            @result: Correct ValidationError is returned
            @step: Attempt to remove non existing "system-param node config"
                from the model
            @result: Correct ValidationError is returned
        @tms_test_precondition:NA
        @tms_execution_type: Automated
        """
        self.log('info', '1. Find the sysparam-node-config already on node1')
        sysparam_node_config = self.find(
            self.test_ms, "/deployments", "sysparam-node-config")[0]

        sysparam_path = sysparam_node_config + "/params/sysctltest02a"

        self.log('info', '2. Attempt to create '
                         'system-param value with an empty string')
        rule_sets = []
        rule_set = {
        'description': '1. Attempt to create system-param value '
                       'with an empty string',
        'param': 'key="" value="02 value"',
        'results':
        [
         {
          'index': 0,
          'path': None,
          'msg': 'ValidationError in property: "key"    Invalid value \'\'.'
          }
         ]
        }
        rule_sets.append(rule_set.copy())

        self.log('info', '3. Attempt to create system-param with key contains')
        rule_set = {
        'description': '2. Attempt to create system-param with key contains ,',
        'param': 'key="kernel.,test02" value="02 value"',
        'results':
        [
         {
          'index': 0,
          'path': None,
          'msg': 'ValidationError in property: "key"    '
                 'Invalid value \'kernel.,test02\'.'
          }
         ]
        }
        rule_sets.append(rule_set.copy())

        self.log('info', '4. Attempt to create '
                         'system-param with key contains =')
        rule_set = {
        'description': '3. Attempt to create system-param with key contains =',
        'param': 'key="kernel=test02" value="02 value"',
        'results':
        [
         {
          'index': 0,
          'path': None,
          'msg': 'ValidationError in property: "key"    '
                 'Invalid value \'kernel=test02\'.'
          }
         ]
        }
        rule_sets.append(rule_set.copy())

        self.log('info', '5. Attempt to create '
                         'system-param value to empty string')
        rule_set = {
        'description': '4. Attempt to create system-param value to '
                       'empty string',
        'param': 'key="kernel.test02" value=""',
        'results':
        [
         {
          'index': 0,
          'path': None,
          'msg': 'ValidationError in property: "value"    Invalid value \'\'.'
          }
         ]
        }
        rule_sets.append(rule_set.copy())

        self.log('info', '6. Attempt to create '
                         'system-param with an additional property')
        rule_set = {
        'description': '5. Attempt to create system-param with an '
                       'additional property',
        'param': 'key="kernel.test02" value="02 test" name="test"',
        'results':
        [
         {
          'index': 0,
          'path': None,
          'msg': 'PropertyNotAllowedError in property: "name"    '
                 '"name" is not an allowed property of sysparam'
          }
         ]
        }
        rule_sets.append(rule_set.copy())

        self.log('info', '7. Attempt to create '
                         'system-param with a missing value property')
        rule_set = {
        'description': '6. Attempt to create system-param with a '
                       'missing value property',
        'param': 'key="kernel.test02"',
        'results':
        [
         {
          'index': 0,
          'path': None,
          'msg': 'MissingRequiredPropertyError in property: "value"    '
                 'ItemType "sysparam" is required to have a property with '
                 'name "value"'
          }
         ]
        }
        rule_sets.append(rule_set.copy())

        self.log('info', '8. Attempt to create '
                         'system-param with missing key property')
        rule_set = {
        'description': '7. Attempt to create system-param with missing '
                       'key property',
        'param': 'value="02 test value"',
        'results':
        [
         {
          'index': 0,
          'path': None,
          'msg': 'MissingRequiredPropertyError in property: "key"    '
                 'ItemType "sysparam" is required to have a property with '
                 'name "key"'
          }
         ]
        }
        rule_sets.append(rule_set.copy())

        for rule in rule_sets:
            self.log("info", "\n*** Starting test for invalid sysparams "
                     "rules data set : {0}"
                     .format(rule['description']))

            _, stderr, _ = self.execute_cli_create_cmd(
                  self.test_ms, sysparam_path, "sysparam", rule['param'],
                  expect_positive=False)

            for result in rule['results']:
                self._assert_err_msg_list(stderr, result)

        self.log('info', '9. Check the same key '
                         'cannot be specified more than once for a node')
        props = ('key="kernel.samekey" value="02a value"')
        self._create_system_param(
            sysparam_node_config, "sysctltest02b", props)

        props = ('key="kernel.samekey" value="02b value"')
        self._create_system_param(
            sysparam_node_config, "sysctltest02c", props)

        rule_sets = []
        rule_set = {
        'description': '8. Check the same key cannot be specified more '
                       'than once for a node',
        'param': None,
        'results':
        [
         {
          'index': 0,
          'path': sysparam_node_config + '/params/sysctltest02b',
          'msg': 'ValidationError    Create plan failed: '
                 'Duplicate sysparam key: kernel.samekey'
          }
         ]
        }
        rule_sets.append(rule_set.copy())

        for rule in rule_sets:
            self.log("info", "\n*** Starting test for invalid sysparams "
                     "rules data set : {0}"
                     .format(rule['description']))

             # Create plan fails with error
            _, stderr, _ = self.execute_cli_createplan_cmd(
                 self.test_ms, expect_positive=False)

            for result in rule['results']:
                self._assert_err_msg_list(stderr, result)

        self.log('info', '10. Attempt to remove the key')
        props = ('key="kernel.newkey02" value="2345"')
        system_param = self._create_system_param(
            sysparam_node_config, "sysctltesttest02b", props)

        props = ('key')

        rule_sets = []
        rule_set = {
        'description': '9. Attempt to remove the key',
        'param': 'key',
        'results':
        [
         {
          'index': 0,
          'path': None,
          'msg': 'MissingRequiredPropertyError in property: "key"    '
                 'ItemType "sysparam" is required to have a property with '
                 'name "key"'
          }
         ]
        }
        rule_sets.append(rule_set.copy())

        self.log('info', '11. Attempt to remove the value')
        props = ('value')

        rule_set = {
        'description': '10. Attempt to remove the value',
        'param': 'value',
        'results':
        [
         {
          'index': 0,
          'path': None,
          'msg':'MissingRequiredPropertyError in property: "value"    '
                'ItemType "sysparam" is required to have a property with '
                'name "value"'
          }
         ]
        }
        rule_sets.append(rule_set.copy())

        for rule in rule_sets:
            self.log("info", "\n*** Starting test for invalid sysparams "
                     "rules data set : {0}"
                     .format(rule['description']))

            _, stderr, _ = self.execute_cli_update_cmd(
                 self.test_ms, system_param, rule['param'], action_del=True,
                 expect_positive=False)

            for result in rule['results']:
                self._assert_err_msg_list(stderr, result)

        self.log('info', '12. Attempt to remove non existing system-param')
        invalid_param = sysparam_node_config + "/params/invaliditem"

        rule_sets = []
        rule_set = {
        'description': '11. Attempt to remove non existing system-param',
        'param': None,
        'results':
        [
         {
          'index': 0,
          'path': invalid_param,
          'msg': 'InvalidLocationError    Path not found'
          }
         ]
        }
        rule_sets.append(rule_set.copy())

        for rule in rule_sets:
            self.log("info", "\n*** Starting test for invalid sysparams "
                     "rules data set : {0}"
                     .format(rule['description']))

            _, stderr, _ = self.execute_cli_remove_cmd(
                   self.test_ms, invalid_param, expect_positive=False)

            for result in rule['results']:
                self._assert_err_msg_list(stderr, result)

        self.log('info', '13. Attempt to remove non '
                         'existing "system-param node config" '
                         'from the model')
        invalid_node_config = sysparam_node_config + "/invalid"
        rule_sets = []
        rule_set = {
        'description': '12. Attempt to remove non existing '
                       '"system-param node config" from the model',
        'param': None,
        'results':
        [
         {
          'index': 0,
          'path': invalid_node_config,
          'msg': 'InvalidLocationError    Path not found'
          }
         ]
        }
        rule_sets.append(rule_set.copy())
        for rule in rule_sets:
            self.log("info", "\n*** Starting test for invalid sysparams "
                     "rules data set : {0}"
                     .format(rule['description']))

            _, stderr, _ = self.execute_cli_remove_cmd(
                   self.test_ms, invalid_node_config, expect_positive=False)

            for result in rule['results']:
                self._assert_err_msg_list(stderr, result)

    @attr('all', 'revert', 'story2327_5774', 'story2327_5774_tc03')
    def test_03_p_update_system_parameter_positive(self):
        """
        @tms_id: litpcds_2327_5774_tc03
        @tms_requirements_id: LITPCDS-2327, LITPCDS-5774
        @tms_title: update and remove a system param
        @tms_description: Test that a value of a key and the key name can be
            updated through the deployment model
        @tms_test_steps:
            @step:  Find a sysparam-node-config
            @result: a sysparam-node-config is found
            @step:  Create sysparm1 with valid key(1)
            @result: sysparm with valid key is created in model
            @step:  Create sysparm2 with invalid key(2)
            @result: sysparm with valid key is created in model
            @step:  Create sysparm3 with valid key(3)
            @result: sysparm with valid key is created in model
            @step:  Check the created sysparams state is "initial"
            @result: all 3 sysparams are in state is "initial"
            @step:  Update sysparam2 which has invalid key(2) to valid updated
            @result: sysparam2 is updated
            @step:  Check the updated sysparam2 state is "initial"
            @result:  sysparam2 state is "initial"
            @step:  Create plan, Run plan
            @result: Plan runs successfully
            @step:  Check the sysparams states are in Applied state.
            @result: sysparams states are in Applied state
            @step: Update the value of the sysparm1
            @result: sysparm1 value is updated
            @step: Update sysparam3 key(3) with key(4)
            @result: sysparam3 key(3) is updated with key(4)
            @step: Create plan
            @result: Create plan fails with correct error message
            @step: remove sysparam3
            @result: sysparam3 is in state ForRemoval
            @step: create plan, Run plan
            @result: Plan runs successfully
            @step: Check the value of the sysparam1 is updated in sysctl.conf
            @result: sysparam1 is updated in the sysctl.conf file
            @step: check syaparam1 value is updated in memory on target node
            @result: syaparam1 value is updated in memory on the target node
            @step: Check sysparam3 key(3) is removed in sysctl.conf
            @result: sysparam3 key(3) is removed in sysctl.conf
            @step: Check sysparam3 key(3) exists in the memory
            @result: sysparam3 key(3) exists in the memory
            @step: Check sysparam3 key(4) is not added in the config file
            @result: sysparam3 key(4) is not added in the config file
        @tms_test_precondition:NA
        @tms_execution_type: Automated
        """

        # Find the path to node1
        n1_path = self.find(
            self.test_ms, "/deployments", "node")[0]

        # Get node1 filename
        test_node1 = self.get_node_filename_from_url(
            self.test_ms, n1_path)

        # Backup sysctl.conf file to tmp_location
        self.assertTrue(self.backup_file(
            test_node1, test_constants.SYSCTL_CONFIG_FILE))

        self.log('info', '1. Find the sysparam-node-config already on node1')
        sysparam_node_config = self.find(
            self.test_ms, "/deployments", "sysparam-node-config")[0]

        # Create sysctl keys required for test
        sysctl_key1 = "kernel.threads-max"
        sysctl_key2 = "kernel.invalid_key"
        sysctl_key3 = "net.ipv4.ip_forward"
        sysctl_updated_key2 = "kernel.pid_max"
        sysctl_key4 = "kernel.update"

        self.log('info', '2.  Create sysparm1 with valid key(1)')
        props1 = 'key="{0}" value="15637"'.format(sysctl_key1)
        sysparam1 = self._create_system_param(
            sysparam_node_config, "sysctltest03a", props1)

        self.log('info', '3.  Create sysparm2 with invalid key(2)')
        props2 = 'key="{0}" value="3276"'.format(sysctl_key2)
        sysparam2 = self._create_system_param(
            sysparam_node_config, "sysctltest03b", props2)

        self.log('info', '4.  Create sysparm3 with valid key(3)')
        props1 = 'key="{0}" value="15"'.format(sysctl_key3)
        sysparam3 = self._create_system_param(
            sysparam_node_config, "sysctltest03c", props1)

        self.log('info', '5.  Check the created sysparams state is "initial"')
        state_value = self.execute_show_data_cmd(
            self.test_ms, sysparam1, "state")
        self.assertEqual(state_value, "Initial")

        state_value = self.execute_show_data_cmd(
            self.test_ms, sysparam2, "state")
        self.assertEqual(state_value, "Initial")

        state_value = self.execute_show_data_cmd(
            self.test_ms, sysparam3, "state")
        self.assertEqual(state_value, "Initial")

        self.log('info', '6. Update sysparam2 which has '
                         'invalid key(2) to valid updated key(2)')
        props = 'key="{0}"'.format(sysctl_updated_key2)
        self._update_system_param_props(
            sysparam_node_config, "sysctltest03b", props)

        self.log('info', '7. Check the updated sysparam2 state is "initial"')
        state_value = self.execute_show_data_cmd(
            self.test_ms, sysparam2, "state")
        self.assertEqual(state_value, "Initial")

        self.log('info', '8. Create plan')
        self.execute_cli_createplan_cmd(self.test_ms)

        self.log('info', '9. Run plan')
        self.execute_cli_runplan_cmd(self.test_ms)

        # Wait for plan to complete
        self.assertTrue(self.wait_for_plan_state(
            self.test_ms, test_constants.PLAN_COMPLETE))

        self.log('info', '10.  Check the sysparams '
                         'states are in Applied state.')
        state_value = self.execute_show_data_cmd(
            self.test_ms, sysparam1, "state")
        self.assertEqual(state_value, "Applied")

        state_value = self.execute_show_data_cmd(
            self.test_ms, sysparam2, "state")
        self.assertEqual(state_value, "Applied")

        state_value = self.execute_show_data_cmd(
            self.test_ms, sysparam3, "state")
        self.assertEqual(state_value, "Applied")

        # Find the created keys in sysctl.conf file
        orig_key1_val = self._find_keyvalue_in_sysctl_conf(
            test_node1, sysctl_key1)

        self.log('info', '11. Update the value of the sysparm1')
        props = ('value="15638"')
        self._update_system_param_props(
            sysparam_node_config, "sysctltest03a", props)

        self.log('info', '12. Update sysparam3 key(3) with key(4)')
        props = 'key="{0}"'.format(sysctl_key4)
        self._update_system_param_props(
            sysparam_node_config, "sysctltest03c", props)

        # Verify that key name cannot be updated
        rule_sets = []
        rule_set = {
        'description': 'Verify that key name cannot be updated',
        'param': None,
        'results':
        [
         {
          'index': 0,
          'path': sysparam_node_config + '/params/sysctltest03c',
          'msg': 'ValidationError    Create plan failed: '
                 'The key name "net.ipv4.ip_forward" cannot be'
                 ' updated. Please remove the item and'
                 ' recreate it.'
          }
         ]
        }
        rule_sets.append(rule_set.copy())

        for rule in rule_sets:
            self.log("info", "\n*** Starting test for invalid sysparams"
                         "rules data set : {0}"
                         .format(rule['description']))

            self.log('info', '13. Create plan')
            _, stderr, _ = self.execute_cli_createplan_cmd(
                 self.test_ms, expect_positive=False)

            for result in rule['results']:
                self.log('info', '14. Check the Error message')
                self._assert_err_msg_list(stderr, result)

        self.log('info', '15. remove sysparam3')
        self.execute_cli_remove_cmd(self.test_ms, sysparam3)

        self.log('info', '16. Create plan')
        self.execute_cli_createplan_cmd(self.test_ms)

        self.log('info', '17. Run plan')
        self.execute_cli_runplan_cmd(self.test_ms)

        # Wait for plan to complete
        self.assertTrue(self.wait_for_plan_state(
            self.test_ms, test_constants.PLAN_COMPLETE))

        self.log('info', '18. Check the value of the sysparam1 is updated in')
        # the sysctl.conf file
        updated_key1_val = self._find_keyvalue_in_sysctl_conf(
            test_node1, sysctl_key1)
        self.assertNotEqual(orig_key1_val, updated_key1_val)

        self.log('info', '19. check syaparam1 value is '
                         'updated in memory on the target node')
        updated_memory_value = self._check_memory_values(test_node1,
                                                         sysctl_key1)
        self.assertEqual(updated_key1_val, updated_memory_value)

        self.log('info', '20. Check sysparam3 key(3) '
                         'is removed in sysctl.conf')
        self._find_keyvalue_in_sysctl_conf(
            test_node1, sysctl_key3, positive=False)

        self.log('info', '21. Check sysparam3 key(3) exists in the memory')
        self._check_memory_values(test_node1, sysctl_key3)

        self.log('info', '22. Check sysparam3 key(4) '
                         'is not added in the config file')
        self._find_keyvalue_in_sysctl_conf(
            test_node1, sysctl_key4, positive=False)

    @attr('all', 'revert', 'story2327_5774', 'story2327_5774_tc04')
    def test_04_p_system_param_export_load_xml(self):
        """
        @tms_id: litpcds_2327_5774_tc04
        @tms_requirements_id: LITPCDS-2327, LITPCDS-5774
        @tms_title: Create a system param with XML
        @tms_description: Verify system parameter can be exported and loaded
        @tms_test_steps:
            @step:  Find a sysparam-node-config
            @result: a sysparam-node-config is found
            @step: Create system-param
            @result: system-param is created in the model
            @step: Export the sysparam-node-config
            @result: sysparam-node-config is exported to an xml file
            @step: Load the sysparam-node-config into model using --merge
            @result: command executes successfully
            @step: Load the sysparam-node-config into model using --replace
            @result: command executes successfully
            @step: Export the system-param
            @result: system-param is exported to a file
            @step: Remove system-param
            @result: system-param is removed from model
            @step: Load the system-param into the model
            @result: system-param is loaded form xml file into model
            @step: Copy xml files onto the MS
            @result: xml files are copied onto MS
            @step: Load xml file using the --merge
            @result: command executes successfully and sysparam are created
            @step: Check the created sysparam state is "initial"
            @result: sysparam state is "initial"
            @step: Load xml file using the --replace
            @result: command executes successfully and sysparams are created
            @step: Create plan, Run plan
            @result: Plan runs successfully and sysparams are created
            @step: Check state of items in tree
            @result: sysparam is now in Applied state
            @step: Check all parameters in xml file exist in conf file
            @result: all parameters in xml file exist in conf file
            @step: Remove all items that were loaded, create & run plan
            @result: sysparams are removed and system is returned to the pre
                test state
        @tms_test_precondition:NA
        @tms_execution_type: Automated
        """
        # Find the desired collection on node1
        collection_type = "collection-of-node-config"
        n1_config_path = self.find(
            self.test_ms, "/deployments", collection_type)[0]
        n1_path = self.find(
            self.test_ms, "/deployments", "node")[0]

        # Get node1 filename
        test_node1 = self.get_node_filename_from_url(
            self.test_ms, n1_path)

        # Backup sysctl.conf file to tmp_location
        self.assertTrue(self.backup_file(
            test_node1, test_constants.SYSCTL_CONFIG_FILE))

        # Create sysctl keys required for test
        sysctl_key1 = "fs.file-max"
        sysctl_key2 = "kernel.threads-max"
        sysctl_key3 = "kernel.msgmnb"
        sysctl_key4 = "kernel.pid_max"

        self.log('info', '1. Find the sysparam-node-config already on node1')
        sysparam_node_config = self.find(
            self.test_ms, "/deployments", "sysparam-node-config")[0]

        self.log('info', '1. Export the sysparam-node-config')
        self.execute_cli_export_cmd(
            self.test_ms, sysparam_node_config, "xml_init_story2327.xml")

        try:
            self.log('info', '2. Create system-param')
            props = "key={0} value='798264'".format(sysctl_key1)
            system_param = self._create_system_param(sysparam_node_config,
                                                 "sysctltest04", props)

            self.log('info', '3. Export the sysparam-node-config')
            self.execute_cli_export_cmd(
                self.test_ms, sysparam_node_config, "xml_04a_story2327.xml")

            self.log('info', '4. Load the sysparam-node-config'
                             ' into model using --merge')
            self.execute_cli_load_cmd(
                self.test_ms, n1_config_path, "xml_04a_story2327.xml",
                "--merge")

            self.log('info', '5. Load the sysparam-node-config'
                             ' into model using --replace')
            self.execute_cli_load_cmd(
                self.test_ms, n1_config_path, "xml_04a_story2327.xml",
                "--replace")

            self.log('info', '6. Export the system-param')
            self.execute_cli_export_cmd(
                self.test_ms, system_param, "xml_04b_story2327.xml")

            self.log('info', '7. Remove system-param')
            self.execute_cli_remove_cmd(self.test_ms, system_param)

            self.log('info', '8. Load the system-param into the model')
            self.execute_cli_load_cmd(
                self.test_ms, sysparam_node_config + "/params",
                "xml_04b_story2327.xml")

            self.log('info', '9. Copy xml files onto the MS')
            # XML file contains
            #   ==> sysctl param item that is in model but whose name has
            #       been updated
            #   ==> sysctl param item that is in model and not in file
            #   ==> an additional sysctl param item that is not in model
            xml_filenames = \
                ['xml_sysparams_story2327.xml']
            local_filepath = os.path.dirname(__file__)
            for xml_filename in xml_filenames:
                local_xml_filepath = local_filepath + "/xml_file/" + \
                    xml_filename
                xml_filepath = "/tmp/" + xml_filename
                self.assertTrue(self.copy_file_to(
                    self.test_ms, local_xml_filepath, xml_filepath,
                    root_copy=True))

            self.log('info', '10. Load xml file using the --merge')
            self.execute_cli_load_cmd(
                self.test_ms, sysparam_node_config,
                "/tmp/xml_sysparams_story2327.xml", "--merge")

            self.log('info', '11. Check the created '
                             'sysparam state is "initial"')
            state_value = self.execute_show_data_cmd(
                self.test_ms, system_param, "state")
            self.assertEqual(state_value, "Initial")

            self.log('info', '12. Load xml file using the --replace')
            self.execute_cli_load_cmd(
                self.test_ms, sysparam_node_config,
                "/tmp/xml_sysparams_story2327.xml", "--replace")

            self.log('info', '13. Create plan')
            self.execute_cli_createplan_cmd(self.test_ms)

            self.log('info', '14. Run plan')
            self.execute_cli_runplan_cmd(self.test_ms)

            # Wait for plan to complete
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_COMPLETE))

            self.execute_cli_removeplan_cmd(self.test_ms)
            self.log('info', '15. Check state of items in tree')
            self.assertTrue(self.is_all_applied(self.test_ms))

            self.log('info', '16. Check all parameters '
                             'in xml file exist in conf file')
            self._find_keyvalue_in_sysctl_conf(
                test_node1, sysctl_key1, positive=False)
            self.assertTrue(self._find_keyvalue_in_sysctl_conf(
                test_node1, sysctl_key2))
            self.assertTrue(self._find_keyvalue_in_sysctl_conf(
                test_node1, sysctl_key3))
            self.assertTrue(self._find_keyvalue_in_sysctl_conf(
                test_node1, sysctl_key4))

        finally:

            self.log('info', '17. Load original exported config')
            self.execute_cli_load_cmd(
                self.test_ms, n1_config_path, "xml_init_story2327.xml",
                "--replace")

            self.log('info', 'Create plan')
            self.execute_cli_createplan_cmd(self.test_ms)

            self.log('info', ' Run plan')
            self.execute_cli_runplan_cmd(self.test_ms)

            self.log('info', ' Wait for plan to complete')
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_COMPLETE))

    @attr('all', 'revert', 'story2327_5774', 'story2327_5774_tc05')
    def test_05_n_update_invalid_parameter_negative(self):
        """
        @tms_id: litpcds_2327_5774_tc05
        @tms_requirements_id: LITPCDS-2327, LITPCDS-5774
        @tms_title: Create and update a readonly system param
        @tms_description: Test result of puppet failing to update key in memory
            i.e. attempt to update the read-only key, net.ipv4.ip_forward
        @tms_test_steps:
            @step: Find a sysparam-node-config
            @result: A sysparam-node-config is found
            @step: Create system-param with new key
            @result: System-param with new key
            @step: Create plan, Run plan
            @result: The plan should fail
            @step: Check sysctl.conf file doesn't contains key
            @result: Sysctl.conf file doesn't contains key
            @step: Check key failed to add parameter
            @result: Key was not added to memory
            @step: Search for the current value of the read only parameters
            @result: Values of read only parameters are recorded.
            @step: Update read only system-param with the key
            @result: System-param are updated in the model
            @step: Create plan, Run plan
            @result: The plan should fail
            @step: Check sysctl.conf file doesn't contains updated value
            @result: Sysctl.conf file doesn't contains updated value
            @step:.Check puppet failed to update a key in memory
            @result: Puppet failed to update a key in memory
        @tms_test_precondition:NA
        @tms_execution_type: Automated
        """
        n1_path = self.find(
            self.test_ms, "/deployments", "node")[0]

        # Get node1 filename
        test_node1 = self.get_node_filename_from_url(
            self.test_ms, n1_path)

        # Backup sysctl.conf file to tmp_location
        self.assertTrue(self.backup_file(
            test_node1, test_constants.SYSCTL_CONFIG_FILE))

        self.log('info', '1. Find the sysparam-node-config '
                         'already on node1')
        sysparam_node_config = self.find(
            self.test_ms, "/deployments", "sysparam-node-config")[0]

        self.log('info', '2. Create system-param with new key')
        sysctl_new_key = "kernel.newkey"
        props = 'key="{0}" value="05 new"'.format(sysctl_new_key)
        self._create_system_param(
            sysparam_node_config, "sysctltest05", props)

        self.log('info', '3. Create plan')
        self.execute_cli_createplan_cmd(self.test_ms)

        self.log('info', '4. Run plan')
        self.execute_cli_runplan_cmd(self.test_ms)

        self.log('info', '5. Check the plan should fail')
        self.assertTrue(self.wait_for_plan_state(
            self.test_ms, test_constants.PLAN_FAILED))

        self.log('info', '6. Check sysctl.con file does not concatins key')
        self._find_keyvalue_in_sysctl_conf(
            test_node1, sysctl_new_key, positive=False)

        self.log('info', '7. Check key failed to add parameter')
        cmd = self.redhatutils.get_sysctl_cmd(
            '{0}'.format(sysctl_new_key))

        rule_sets = []
        rule_set = {
        'description': 'Checking if "kernel.newkey" is an '
                       'unknown key',
        'param': None,
        'results':
        [
         {
          'index': 0,
          'path': None,
          'msg': 'sysctl: cannot stat /proc/sys/kernel/newkey:'\
                                        ' No such file or directory',
          }
         ]
        }
        rule_sets.append(rule_set.copy())

        for rule in rule_sets:
            self.log("info", "\n*** Starting test for invalid sysparams "
                     "rules data set : {0}"
                     .format(rule['description']))

            stdout, stderr, rc = self.run_command(test_node1,
                                 cmd, su_root=True)

            self.assertEquals([], stderr)
            self.assertNotEqual([], stdout)
            self.assertEquals(255, rc)

            for result in rule['results']:
                self._assert_err_msg_list(stdout, result)

        # Create sysctl keys required for test
        sysctl_key = "net.ipv4.conf.default.mc_forwarding"

        self.log('info', '8. Search for the current '
                         'value of the read only parameter,')
        #    net.ipv4.conf.default.mc_forwarding.
        orig_sysctl_key = self._find_values_sysctl(test_node1, sysctl_key)

        self.log('info', '9. Create system-param with the key, '
                         'net.ipv4.conf.default.mc_forwarding and '
                         'with a value other than the value currently'
                         ' in the sysctl.conf file')
        props = 'key="{0}" value="1"'.format(sysctl_key)
        self._update_system_param_props(
            sysparam_node_config, "sysctltest05", props)

        self.log('info', '10. Create plan')
        self.execute_cli_createplan_cmd(self.test_ms)

        self.log('info', '11. Run plan')
        self.execute_cli_runplan_cmd(self.test_ms)

        self.log('info', '12. Check the plan should fail')
        self.assertTrue(self.wait_for_plan_state(
            self.test_ms, test_constants.PLAN_FAILED))

        self.log('info', '13. Check sysctl.conf file failed to updated value')
        updated_sysctl_key = self._find_values_sysctl(test_node1, sysctl_key)
        self.assertEqual(orig_sysctl_key, updated_sysctl_key)

        self.log('info', '14. Check puppet failed to update a key in memory')
        cmd = self.redhatutils.get_sysctl_cmd(
            '{0}'.format(sysctl_key))
        stdout, stderr, rc = self.run_command(test_node1, cmd, su_root=True)
        self.assertEquals([], stderr)
        self.assertFalse([], stdout)
        self.assertEquals(0, rc)
        self.assertEqual(orig_sysctl_key, stdout[0])

    @attr('all', 'revert', 'story2327_5774', 'story2327_5774_tc06')
    def test_06_p_create_remove_system_param_with_slash(self):
        """
        @tms_id: litpcds_2327_5774_tc06
        @tms_requirements_id: LITPCDS-2327, LITPCDS-5774
        @tms_title: Create and remove a system param with a slash
        @tms_description: Test that an key containing a slash can be
            configured and removed through the deployment model
        @tms_test_steps:
            @step: Find sysparam-node-config already on node1
            @result: Sysparam-node-config is found in model
            @step: Create system-param on node1 with key containing a slash
            @result: System-param with key containing a slash defined in model
            @step: Create plan, Run plan
            @result: Plan runs successfully
            @step: Check sysctl.conf file on node1 contains the key with slash
            @result: Sysctl.conf file on node1 contains the key
            @step: Remove the system-param item-types that have been created
            @result: System-param is in ForRemoval state
            @step: Create plan, Run plan
            @result: Plan runs successfully
            @step:Check the key has been removed from sysctl.conf file
            @result: Key has been removed from sysctl.conf file
        @tms_test_precondition:NA
        @tms_execution_type: Automated
        """

        # Find the desired collection on nodes
        nodes_path = self.find(self.test_ms, "/deployments", "node", True)
        node1_path = nodes_path[0]
        test_node1 = self.get_node_filename_from_url(self.test_ms, node1_path)

        # Create sysctl keys required for test
        sysctl_key1 = "net/ipv4/ip_forward"
        sysctl_filekey1 = "net.ipv4.ip_forward"

        # Create sysctl values required for test
        sysctl_value1 = "599"

        # copy sysctl.conf file to tmp_location
        local_config_filepath = test_constants.SYSCTL_CONFIG_FILE
        config_filepath = "/tmp/sysctl"
        self.assertTrue(self.cp_file_on_node(
            test_node1, local_config_filepath, config_filepath,
            su_root=True))

        try:
            self.log('info', '1. Find the sysparam-node-config'
                             ' already on node1')
            sysparam_node1_config = self.find(
                self.test_ms, "/deployments", "sysparam-node-config")[0]

            self.log('info', '2.  Create system-param'
                             ' on node1 with preexisting '
                             'key(a) in the file')
            props = 'key="{0}" value="{1}"'.format(sysctl_key1, sysctl_value1)
            system_param1 = self._create_system_param(
                sysparam_node1_config, "sysctltest06a", props)

            self.log('info', '3. Create plan')
            self.execute_cli_createplan_cmd(self.test_ms)

            self.log('info', '4. Run plan')
            self.execute_cli_runplan_cmd(self.test_ms)

            # Wait for plan to complete
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_COMPLETE))

            self.log('info', '5. Check sysctl.conf file'
                             ' contains updated preexisting key(a)'
                             ' to the value on node1')
            key1_val = self._find_keyvalue_in_sysctl_conf(
                test_node1, sysctl_key1)
            self.assertEqual(key1_val, sysctl_key1 + " = " + sysctl_value1)

            self.log('info', '6. Remove the system-param'
                             ' item-types that have been created'
                             ' and remove manually updated key(c)')
            self.execute_cli_remove_cmd(self.test_ms, system_param1)

            self.log('info', '7. Create plan')
            self.execute_cli_createplan_cmd(self.test_ms)

            self.log('info', '8. Run plan')
            self.execute_cli_runplan_cmd(self.test_ms)

            # Wait for plan to complete
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_COMPLETE))

            self.log('info', '9.Check the key has been removed'
                             ' from sysctl.conf file')
            self._find_keyvalue_in_sysctl_conf(
                test_node1, sysctl_key1, positive=False)

            self.log('info', '10.Check the key is not removed from memory')
            self._check_memory_values(test_node1, sysctl_filekey1)

        finally:

            # copy  back sysctl.conf
            local_config_filepath = test_constants.SYSCTL_CONFIG_FILE
            config_filepath = "/tmp/sysctl"
            self.assertTrue(self.cp_file_on_node(
                test_node1, config_filepath, local_config_filepath,
                su_root=True))

            # Load the sysctl.conf file on node1
            cmd = self.redhatutils.get_sysctl_cmd(
                '-e -p {0}'.format(test_constants.SYSCTL_CONFIG_FILE))
            stdout, stderr, rc = self.run_command(
                test_node1, cmd, su_root=True)
            self.assertEquals([], stderr)
            self.assertNotEqual([], stdout)
            self.assertEquals(0, rc)
