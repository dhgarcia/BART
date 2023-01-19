#!/usr/bin/env python3

#BART
#
# condition:          [   ]
# results directory : [   ]
# robot IP :          [   ]
# robot port :        [   ]

import os
import ipaddress
import tkinter as tk
from tkinter.ttk import Combobox
from tkinter.messagebox import showerror, showinfo
from tkinter.filedialog import askdirectory

import docker

BART_IMAGE="bart:naoqi-2.5.5"
# BART_IMAGE="bart:naoqi-2.8.6"


base_dir = os.path.dirname(os.path.realpath(__file__))


class MainFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.path = tk.StringVar()
        self.path.set(os.getcwd())

        # self.options = {'padx': 5, 'pady': 5}
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=4)
        self.columnconfigure(2, weight=4)
        self.columnconfigure(3, weight=4)
        self.columnconfigure(4, weight=4)
        self.columnconfigure(6, weight=6)
        # self.rowconfigure(1, weight=1)

        self.createWidgets()
        # show the frame on the container
        # self.pack(**self.options)
        self.grid()

    def createWidgets(self):
        self.medialLabel = tk.Label(self, text='BART Study', font='bold')
        # self.medialLabel.config(bg="#00ffff")
        self.medialLabel.grid(column=0, row=0, padx=15, pady=15, columnspan=4, sticky=tk.EW)
        # self.medialLabel.pack(**self.options)

        # condition
        self.conditionLabel = tk.Label(self, text = "Condition : ")
        self.conditionLabel.grid(column = 0, row = 1, padx = 5, pady = 5)
        self.condition = Combobox(self, values=["Control", "Control (Robot)", "Discourage", "Encourage"], justify=tk.CENTER)
        self.condition.current(0)
        self.condition.grid(column=1, row=1, padx=5, pady=5, columnspan=4, sticky=tk.EW)

        # directory
        self.directoryLabel = tk.Label(self, text = "Results Directory : ")
        self.directoryLabel.grid(column = 0, row = 2, padx = 5, pady = 5)
        self.directoryEntry = tk.Entry(self, justify=tk.CENTER, state=tk.DISABLED, textvariable=self.path)
        # self.directoryEntry.insert(0, self.path)
        self.directoryEntry.grid(column=1, row=2, padx=5, pady=5, columnspan=2)
        self.directoryButton = tk.Button(self, text='Browse', command=self.select_directory)
        self.directoryButton.grid(column=3, row=2, padx=5, pady=5, sticky=tk.E)

        # ip
        self.ipLabel = tk.Label(self, text = "Robot IP : ")
        self.ipLabel.grid(column = 0, row = 3, padx = 5, pady = 5)
        self.ipEntry = tk.Entry(self, justify=tk.CENTER)
        self.ipEntry.insert(0,'192.168.1.100')
        self.ipEntry.grid(column=1, row=3, padx=5, pady=5, columnspan=4, sticky=tk.EW)

        # port
        self.portLabel = tk.Label(self, text = "Robot Port : ")
        self.portLabel.grid(column = 0, row = 4, padx = 5, pady = 5)
        self.portEntry = tk.Entry(self, justify=tk.CENTER)
        self.portEntry.insert(0,'9559')
        self.portEntry.grid(column=1, row=4, padx=5, pady=5, columnspan=4, sticky=tk.EW)


        # run
        tk.Label(self, text = "").grid(column = 0, row = 5, padx = 5, pady = 15)

        self.runLabel = tk.Label(self, text = "Run Experiment ", justify=tk.RIGHT)
        self.runLabel.grid(column = 0, row = 6, padx = 5, pady = 15, columnspan=2)

        self.button = tk.Button(self, text='Start')
        self.button['command'] = self.run_experiment
        self.button.grid(column=2, row=6, padx=5, pady=5)
        # self.button.pack(**self.options)

        self.quitButton = tk.Button(self, text='Quit', command=self.quit)
        self.quitButton.grid(column=3, row=6, padx=5, pady=5, sticky=tk.E)
        # self.quitButton.pack(**self.options)



    def select_directory(self):
        path = askdirectory(title="Choose Directory", initialdir=os.getcwd(), mustexist=True)
        self.path.set(path)
        # self.directoryEntry.insert(0, self.path)


    def check_conditions(self):
        self.command = 'bash'

        if not os.path.isdir(self.directoryEntry.get()):
            showerror(title="Error!", message=f"Results Directory does not exist!", )
            return False

        condition = self.condition.get()
        if condition=="Control":
            # self.command = f"python BART_control.py"
            self.command = f"python BART_app.py --condition control"
        elif condition=="Control (Robot)":
            # self.command = f"python BART_robotcontrol.py"
            self.command = f"python BART_app.py --condition robot"
        elif condition=="Discourage":
            # self.command = f"python BART_discouragerisk.py"
            self.command = f"python BART_app.py --condition discourage"
        elif condition=="Encourage":
            # self.command = f"python BART_encouragerisk.py"
            self.command = f"python BART_app.py --condition encourage"
        # elif condition=="choregraphe":
        #     command = f"choregraphe"
        # elif condition=="naoqi":
        #     command = f"naoqi"
        else:
            showerror(title="Error!", message=f"Condition {condition} is not valid!", )
            return False

        if condition!="Control":
            if self.portEntry.get().isdigit():
                if int(self.portEntry.get()) <= 1024 or int(self.portEntry.get()) > 65535:
                    showerror(title="Error!", message=f"Robot Port {self.portEntry.get()} is not valid!", )
                    return False
            else:
                showerror(title="Error!", message=f"Robot Port {self.portEntry.get()} is not valid!", )
                return False

            try:
                ipaddress.ip_address(self.ipEntry.get())
            except ValueError:
                showerror(title="Error!", message=f"Robot IP {self.ipEntry.get()} is not valid!", )
                return False


        return True


    def run_experiment(self):
        if not self.check_conditions():
            return

        # GET DOCKER
        try:
            client = docker.from_env()
        except Exception as e:
            showerror(title="Error!", message=f"{e}", )
            return

        # Stop any previous BART containers
        try:
            for container in client.containers.list(all=True, filters={'name':'bart'}):
                container.kill()
                container.wait(condition="removed")
        except Exception as e:
            showerror(title="Error!", message=f"{e}", )
            return

        # Check if BART image exist and load it if it doesn't
        try:
            client.images.get(BART_IMAGE)
        except Exception as e:
            # showerror(title="Error!", message=f"docker image not there", )
            # Load image
            # try:
            if not self.load_docker_image(client, os.path.join(base_dir, f"resources/{BART_IMAGE.replace(':','_')}.tar.gz")):
                # client.images.load(os.path.join(base_dir, f"resources/{BART_IMAGE.replace(':','_')}.tar"))
            # except Exception as e:
                showerror(title="Error!", message=f"Could not load docker image {BART_IMAGE}", )
                return


        try:
            client.containers.run(image=BART_IMAGE, remove=True,
            # runtime="nvidia",
                            command=self.command, name="bart", network_mode="host",
                            devices=["/dev/dri:/dev/dri", "/dev/input:/dev/input", "/dev/snd:/dev/snd"],
                            environment={"DISPLAY" : os.environ.get('DISPLAY'),
                                         "NAO_IP"  : self.ipEntry.get(),
                                         "NAO_PORT": self.portEntry.get(),
                                        #  "NVIDIA_DRIVER_CAPABILITIES" : "compute,utility,graphics",
                                        },
                            volumes=['/tmp/.X11-unix:/tmp/.X11-unix:rw',
                                     f'{self.directoryEntry.get()}:/bart/results',
                                    ],
                            )
        except Exception as e:
            print(f"error {e}")
            showerror(title="Error!", message=f"{e}", )
            return


        while True:
            try:
                if client.containers.get("bart").status == 'running':
                    continue
                else:
                    break
            except Exception as e:
                break
        showinfo(title="BART!", message=f"BART experiment ended.", )



    def load_docker_image(self, client, image_path):
        load_popup = tk.Tk()
        load_popup.wm_title("Docker image not found!")
        load_popup.geometry("320x100");
        label = tk.Label(load_popup, text="Loading the docker image ... \nThis may take a while", font='bold')
        label.pack(side="top", fill="x", pady=10)
        # B1 = tk.Button(popup, text="Okay", command = popup.destroy)
        # B1.pack()
        # popup.mainloop()
        try:
            load_popup.update()
            with open(image_path, 'rb') as data:
                client.images.load(data)
        except Exception as e:
            showerror(title="Error!", message=f"{e}. Could not load docker image {image_path}", )
        finally:
            # load_popup.quit()
            load_popup.destroy()

            try:
                client.images.get(BART_IMAGE)
            except Exception as e:
                return False
            else:
                return True




class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # configure the root window
        self.title('BART Study Launcher')
        # self.geometry('300x100')
        # self.iconbitmap('@boom.bmp')
        self.wm_iconphoto(True, tk.PhotoImage(file=os.path.join(base_dir, 'resources/boom.png')))



if __name__ == "__main__":
    os.system("xhost +local:docker")

    app = App()
    frame = MainFrame(app)
    app.mainloop()