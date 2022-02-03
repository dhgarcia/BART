

import os
import datetime
import csv

import operator

class records(object):
    """docstring for records."""
    def __init__(self, rec):
        super(records, self).__init__()

        self.id = None
        self.ballons = []

        for r in rec:
            if r[0] == "Participant ID ":
                try:
                    self.id = int(r[1])
                except:
                    print("Illegal Participant ID")
                    return
            elif r[0] == "Robot present ":
                if r[1] == " no ":
                    self.condt = "Tablet"
                else:
                    self.condt = "None"
            elif r[0] == "Type ":
                if r[1] == " careful robot":
                    self.condt = "Silent"
                if r[1] == " incite robot ":
                    self.condt = "Incite"
            elif r[0] == "Date ":
                self.date = datetime.datetime.strptime(r[1], " %d/%m/%y").date()
            elif r[0] == "Start time ":
                self.start = datetime.datetime.strptime(":".join(r[1:]), " %H:%M").time()
            elif r[0] == "End time ":
                self.end = datetime.datetime.strptime(":".join(r[1:]), " %H:%M ").time()
            elif r[0] == "Elapsed time ":
                self.time = float(r[1].replace(' [s] ',''))
            elif r[0] == "Total reward ":
                self.reward = float(r[1])
            elif r[0] == "score ":
                self.score = float(r[1])
            elif r[0] == []:
                continue
            else:
                if r[0].startswith("balloon number"):
                    rr = r[0].replace(" [0",'') + r[1].replace("no",'') + r[2].replace("yes",'')
                    self.ballons.append([rr.replace("/1]",'')])
                    #print(rr.replace("/1]",''))
                else:
                    self.ballons.append(r)


        # if self.id is not None:
        #     #print(self.date.strftime("%m-%d-%Y"))
        #     print(self.condt)
        #
        #     reader = csv.reader([item for sublist in self.ballons[1:31] for item in sublist]  )
        #
        #     for row in reader:
        #         if row:
        #             print(row)


    def to_csv(self):
        rec = [self.id, self.condt, self.reward, self.score, self.time, self.date.strftime("%m-%d-%Y"), self.start, self.end]
        reader = csv.reader([item for sublist in self.ballons[1:31] for item in sublist]  )
        for row in reader:
            row.pop(0)
            rec = rec + row
        #return [self.id, self.condt, self.reward, self.score, self.time, self.date.strftime("%m-%d-%Y"), self.start, self.end]
        return rec


results_directory = "results/"

if __name__ == "__main__":

    files = os.listdir(results_directory)

    if not [file for file in files if file.startswith("results_") and file.endswith(".txt")]:
        print("Warning! We could not find file in {} directory.".format(results_directory))
    else:
        participant = []
        for file in files:
            rec = []
            with open(os.path.join(results_directory,file), newline='') as f:
                reader = csv.reader(f, delimiter=':', quoting=csv.QUOTE_NONE)
                for row in reader:
                    if row:
                        rec.append(row)
                    #print(row)
            rc = records(rec)
            if rc.id is not None:
                participant.append(rc)
        print("Read records from {} participants".format(len(participant)))

    participant = sorted(participant, key=operator.attrgetter('id'))
    headers = ["ID", "condition", "reward", "score", "time", "date", "start", "end"]
    balloon_headers = ["intervention","verbal_interventions","pumps", "explosion_point", "exploded", "payment"]
    for i in range(1, 31):
        for h in balloon_headers:
            headers.append("balloon_{}_{}".format(i, h))

    with open('BART_results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for p in participant:
            writer.writerow(p.to_csv())
