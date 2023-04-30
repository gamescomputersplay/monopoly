def analyze_results(results, sim_conf):
    """Analize results"""

    remainingPlayers = [
        0,
    ] * sim_conf.n_players

    for result in results:
        alive = 0
        for score in result:
            if score >= 0:
                alive += 1
        remainingPlayers[alive - 1] += 1

    if sim_conf.show_rem_players:
        print("Remaining:", remainingPlayers)


def analyze_data():
    if (
        writeData == "losersNames"
        or writeData == "experiment"
        or writeData == "remainingPlayers"
    ):
        groups = {}
        with open("data.txt", "r") as fs:
            for line in fs:
                item = line.strip()
                if item in groups:
                    groups[item] += 1
                else:
                    groups[item] = 1
        experiment = 0
        control = 0
        for item in sorted(groups.keys()):
            count = groups[item] / nSimulations

            if writeData == "losersNames":
                count = 1 - count
            if item == "exp":
                experiment = count
            else:
                control += count

            margin = 1.96 * math.sqrt(count * (1 - count) / nSimulations)
            print("{}: {:.1%} +- {:.1%}".format(item, count, margin))

        if experiment != 0:
            print("Exp result: {:.1%}".format(experiment - control / (nPlayers - 1)))

    if writeData == "net_worth":
        print("graph here")
        npdata = np.loadtxt("data.txt", dtype=int)
        print(npdata)
        x = np.arange(0, max([len(d) for d in npdata]))

        plt.ioff()
        fig, ax = plt.subplots()
        for i in range(nPlayers):
            ax.plot(x, npdata[i], label="1")
        plt.savefig("fig" + str(time.time()) + ".png")

    if writeData == "lastTurn":
        npdata = np.transpose(np.loadtxt("data.txt", dtype=int, delimiter="\n"))
        # x = np.arange(0, max([len(d) for d in npdata]))

        plt.ioff()
        fig, axs = plt.subplots(tight_layout=True)
        axs.hist(npdata, bins=20)

        plt.savefig("fig" + str(time.time()) + ".png")
