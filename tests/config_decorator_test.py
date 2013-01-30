import unittest
import webracer

class ConfigDecoratorTest(unittest.TestCase):
    def test_config_decorator(self):
        @webracer.config(host='decoratortesthost', port=5544)
        class test_class(webracer.WebTestCase):
            def test_noop(self):
                pass
        
        instance = test_class('test_noop')
        config = instance.config
        self.assertEqual('decoratortesthost', config.host)
        self.assertEqual(5544, config.port)
    
    def test_multiple_config_decorators(self):
        @webracer.config(host='decoratortesthost', port=5541)
        @webracer.config(user_agent='decoratortestua')
        class test_class(webracer.WebTestCase):
            def test_noop(self):
                pass
        
        instance = test_class('test_noop')
        config = instance.config
        self.assertEqual('decoratortesthost', config.host)
        self.assertEqual(5541, config.port)
        self.assertEqual('decoratortestua', config.user_agent)

if __name__ == '__main__':
    import unittest
    unittest.main()
