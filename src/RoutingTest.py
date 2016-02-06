#!/usr/bin/env python2

import unittest
import json
from lxml import etree

__unittest = True


class RoutingTest(unittest.TestCase):
    def __init__(self, testname, filename):
        super(RoutingTest, self).__init__(testname)
        self.filename = filename

    def setUp(self):

        with open('Configuration.json') as data_file:
            self.config = json.load(data_file)

        self.root = etree.parse(self.filename).getroot()

    def test_variable_format(self):

        self.assertGenesysVariableFormat(self.root, "./version/variables")

    def test_unlinked_objects(self):

        self.assertGenesysUnlinkedObjects(self.root, "./version/objects")

    def assertGenesysVariableFormat(self, node, xpath):
        """Asserts each xpaths value is in the expected format."""
        vnamexpath = xpath + '/row/varName/string/@value'
        variablenames = node.xpath(vnamexpath)

        for vname in variablenames:
            result = vname.split(self.config['variables']['delimiter'])

            if not result:
                self.fail('Invalid delimiters found for variable name: %s\n'
                          'Expected Delimiter: %s\n'
                          % (vname, self.config['variables']['delimiter']))

            if result[0] != self.config['variables']['prepender']:
                self.fail('Invalid value found for variable name: %s\n'
                          'Prepender value found: %s\n'
                          'Expected Value: %s\n'
                          % (vname, result[0], self.config['variables']['prepender']))

            scopename = node.xpath(xpath + "/row[contains(varName/string/@value,'" + vname + "')]/scope/string/@value")
            if result[1] != self.config['variables']['scope'][scopename[0]]:
                self.fail('Invalid value found for variable name: %s\n'
                          'Scope value found: %s\n'
                          'Expected Value: %s\n'
                          % (vname, result[1], self.config['variables']['scope'][scopename[0]]))

            typename = node.xpath(xpath + "/row[contains(varName/string/@value,'" + vname + "')]/type/string/@value")
            if result[2] != self.config['variables']['type'][typename[0]]:
                self.fail('Invalid value found for variable name: %s\n'
                          'Scope value found: %s\n'
                          'Expected Value: %s\n'
                          % (vname, result[2], self.config['variables']['type'][typename[0]]))

    def assertGenesysUnlinkedObjects(self, node, xpath):

        for obj in self.config['object_types']:

            miscobj = len(node.xpath(xpath + obj))
            if miscobj >= 1:
                miscobjnext = node.xpath(xpath + obj + '/@next')
                # print obj + "(" + str(miscobj) + ") : " + str(miscobjnext)

                if len(miscobjnext) != miscobj:
                    self.assertEquals(obj, '/miscExit',
                                      'This objectType is missing a connection out the Green Port: %s\n' % obj)

                miscobjdefaultnext = node.xpath(xpath + obj + '/@defaultNext')
                # print obj + "(" + str(miscobj) + ") : " + str(miscobjdefaultnext)

                if len(miscobjdefaultnext) != miscobj:
                    self.assertFalse(obj == '/miscMacro'
                                            or obj == '/multiFunction'
                                            or obj == '/miscSubroutine'
                                            or obj == '/miscIf'
                                            or obj == '/misc',
                                            'This objectType is missing a connection out the Red Port: %s\n' % obj)
def suite():
    ste = unittest.TestSuite()
    ste.addTest(RoutingTest('test_variable_format', 'Global_Inbound.xml'))
    ste.addTest(RoutingTest('test_unlinked_objects', 'Global_Inbound.xml'))
    return ste

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run(test_suite)
