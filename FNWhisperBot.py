import fortnitepy
import datetime
import os
import asyncio
import threading

from fortnitepy.ext import commands

import json

def time() -> str:
    '''Return current system datetime as string.'''
    return datetime.datetime.now().strftime('%H:%M:%S')


class KeyboardThread(threading.Thread):

    def __init__(self, input_cbk = None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name)
        self.paused = False
        # Explicitly using Lock over RLock since the use of self.paused
        # break reentrancy anyway, and I believe using Lock could allow
        # one thread to pause the worker, while another resumes; haven't
        # checked if Condition imposes additional limitations that would 
        # prevent that. In Python 2, use of Lock instead of RLock also
        # boosts performance.
        self.pause_cond = threading.Condition(threading.Lock())
        self.start()

    def run(self):
        while True:
            with self.pause_cond:
                while self.paused:
                    self.pause_cond.wait()
            self.input_cbk(input('epic-id:message\\')) #waits to get input + Return

    def pause(self):
        self.paused = True
        # If in sleep, we acquire immediately, otherwise we wait for thread
        # to release condition. In race, worker will still see self.paused
        # and begin waiting until it's set back to False
        self.pause_cond.acquire()

    #should just resume the thread
    def resume(self):
        self.paused = False
        # Notify so thread will wake after lock released
        self.pause_cond.notify()
        # Now release the lock
        self.pause_cond.release()


class WhisperClient(fortnitepy.Client):
    def __init__(self, data):
        self.data = data
        device_auth_details = self.get_device_auth_details().get(self.data["email"], {})
        super().__init__(
            auth = fortnitepy.AdvancedAuth(
                email = self.data["email"],
                password = self.data["password"],
                prompt_authorization_code = True,
                delete_existing_device_auths = True,
                **device_auth_details
            )
        ) 
        
    def get_device_auth_details(self):
        if os.path.isfile(self.data["auth_filename"]):
            with open(self.data["auth_filename"], 'r') as fp:
                return json.load(fp)
        return {}

    def store_device_auth_details(self, details):
        existing = self.get_device_auth_details()
        existing[self.data["email"]] = details
        with open(self.data["auth_filename"], 'w') as fp:
            json.dump(existing, fp)
            
    async def event_device_auth_generate(self, details, email):
        self.store_device_auth_details(details)
        
    def get_friends_list(self):
        for f in self.friends:
            if(f.is_online):
                print(f'Friend name: {f.display_name}, Epic-ID: {f.id}')
        return([x.id for x in self.friends])

    async def event_ready(self):
        #print ready status
        print('----------------')
        print('Client ready as')
        print(self.user.display_name)
        print(self.user.id)
        print('----------------')
        self.friendslist = self.get_friends_list()
        #starting loop task
        loop = asyncio.get_event_loop()
        loop.create_task(self.chat_task())
        self.message_text = ''
        self.kbd_thread = KeyboardThread(self.get_input)

    async def event_friend_presence(self, before, after):
        pass

    async def event_party_invite(self, invite):
        print(f'\n{time()}: incoming invite from {invite.sender.display_name}, id {invite.sender.id}')
        if(not(self.data["invite_accept"])):
            await invite.sender.send('Sorry, currently I am not accepting invites.')
            await invite.decline()
            print(f'{time()}: declined party invite from {invite.sender.display_name}, id {invite.sender.id}. Invite_accept is set to false.')
            return
        else:
            await invite.accept()
            print(f'{time()}: accepted party invite from {invite.sender.display_name}, id {invite.sender.id}.')
    
    async def event_party_update(self, party):
        for member in party.members:
            if(not(member.id == self.user.id)):
                print(f'{time()}: {member.display_name} joined wearing outfit {member.outfit} and pickaxe {member.pickaxe}')

    async def chat_task(self):
        while True:
            try:
                if(len(self.message_text)>0):
                    await self.send_message()
                if(self.kbd_thread.paused):
                    self.kbd_thread.resume()
            except:
                print(f'{time()}: error in chat cyclic task')
            await asyncio.sleep(1)

    async def send_message(self):
        msg_items = self.message_text.split(':')
        self.message_text = ''
        if(len(msg_items)<2):
            print('please use the following format:"epic-id:message"')
            return
        if(msg_items[0] in self.friendslist):
            friend = [f for f in self.friends if f.id == msg_items[0]]
        await friend[0].send(msg_items[1])

    def get_input(self, inp):
        self.message_text = inp
        self.kbd_thread.pause()

    async def event_friend_request(self, request):
        if self.data["friend_accept"]:
            await request.accept()
            print(time() + ' accepted friend request from {} ID {}'.format(request.display_name, request.id))

    async def event_friend_message(self, message):
        self.kbd_thread.pause()
        print('\r' + time() + ': {0.author.display_name} ({0.author.id}): "{0.content}"'.format(message))
        print('epic-id:message\\')
        self.kbd_thread.resume()

def main():
    with open('config.json') as f:
        data = json.load(f)
    data["email"] = input('please enter e-mail:')
    data["password"] = input('please enter password:')
    client = WhisperClient(data)
    client.run()

main()