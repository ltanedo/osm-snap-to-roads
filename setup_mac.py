import subprocess


'''
Setup Commands - FOR MAC
'''
#1 /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
# subprocess.run(["/usr/bin/ruby", "-e", '"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"'])

#2 brew cask install adoptopenjdk
subprocess.run(["brew", "cask", "install", "adoptopenjdk"])

#3 brew install maven
subprocess.run(["brew", "install", "maven"])

#4 mvn package -DskipTests
subprocess.run(["mvn", "package", "-DskipTests"])

