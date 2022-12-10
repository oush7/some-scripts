from icmplib import ICMPRequest, ICMPv4Socket, resolve, ICMPLibError

def traceroute(destination, ttl=64, timeout=5, num_of_req=3):
    try:
        destination_ip = resolve(destination)
    except Exception:
        print('Wrong address. Try again...\n')
        exit()

    print(f'ip : {destination_ip[0]}\n')
    curr_iter = 1
    curr_ip = ''

    # Create an ICMP socket
    socket = ICMPv4Socket(privileged=False)

    while curr_iter <= ttl and curr_ip != destination_ip[0]:

        print(curr_iter, end=' ')
        source_printed = False
        for iter in range(num_of_req):
            try:
                # Create an ICMP echo request
                icmp_echo_request = ICMPRequest(destination_ip[0], id=iter, sequence=iter, ttl=curr_iter)

                # Send request
                socket.send(icmp_echo_request)

                # Get reply
                reply = socket.receive(icmp_echo_request, timeout=timeout)
                curr_ip = reply.source
                round_trip_time = (reply.time - icmp_echo_request.time) * 1000
                if not source_printed:
                    print(f'{reply.source} ', end='')
                    source_printed = True
                print(f'{round(round_trip_time, 3)} ms', end=' ')
            except ICMPLibError as err:
                print('*', end=' ')
        print('\n')
        curr_iter += 1

if __name__ == '__main__':
    destination = str(input("Enter destination : "))
    print()
    traceroute(destination)
