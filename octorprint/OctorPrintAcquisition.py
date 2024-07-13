from octorest import OctoRest
def make_client():
    try:
        client = OctoRest(url="http://172.16.25.206", apikey="0BF62B17FF5F4997B41692C9E1D90FB7")
        return client
    except Exception as e:
        print(e)

def get_version():
    client = make_client()
    message = "You are using OctoPrint v" + client.version['server'] + "\n"
    return message

def get_printer_info():
    try:
        client = OctoRest(url="http://172.16.25.206", apikey="0BF62B17FF5F4997B41692C9E1D90FB7")
        message = ""
        message += str(client.version) + "\n"
        message += str(client.job_info()) + "\n"
        printing = client.printer()['state']['flags']['printing']
        info = client.printer()
        bed_temperature = float(info['temperature']['bed']['actual'])
        tool_temperature = float(info['temperature']['tool0']['actual'])
        if printing:
            message += "Currently printing!\n"
        else:
            message += "Not currently printing...\n"
        return printing, bed_temperature, tool_temperature
    except Exception as e:
        print(e)