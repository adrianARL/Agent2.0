import hug

class API:

    def __init__(self, agent):
        self.agent = agent

    @hug.get('/home')
    def root():
        return 'Welcome home!'
