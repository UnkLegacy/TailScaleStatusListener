from tailscalemonitor import TailscaleMonitor

def main():
    """Entry point"""
    monitor = TailscaleMonitor()
    monitor.run()


if __name__ == "__main__":
    main()