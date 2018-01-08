#! /usr/bin/python
# -*-coding:UTF-8-*-

'''
Creaated on 2018-01-01
@author {wrf：wurifeng0531@163.com}

环境：Python 2.7
版本：1.0.0.20180102
1.功能描述：
	1.递归查找指定路径下的程序源文件，计算每个文件的行数和所有文件的总行数（除去空行和注释）。
	2.可指定日期，计算目标是创建日期大于指定日期的文件。
	3.不指定日期，输入参数设为ALL，则计算目标是指定路径下所有文件。
	4.计算结果在cmd控制台打印出来，同时存入line.txt（与本文件在同一路径）.
2.目前实现：
	计算.py .cpp .c .h四类文件
3.使用方法：
	1.在cmd中，进到本文件所在的路径，执行命令linesCounter.py 路径 日期
	2.路径为绝对路径或相对路径
	3.日期的格式：月份（缩写）-日期-时:分:秒-年
	4.命令示例：
		linesCounter.py VTS_DLL ALL
		linesCounter.py VTS_DLL Oct-01-00:00:00-2017
4.特别说明：
	对于python文件，默认开头#！解释器说明和中文编码说明这两行如果有的话写在前两行;不处理“这两行之间有若干空行”的写法.
'''

import os
#import sys
import string
import time

class LinesCounter :
	def __init__(self, path, timeStamp) :
		print "I am a lines counter!"
		self.__alphas = string.ascii_letters + '_'
		self.__alphasAndNums = self.__alphas + string.digits
		self.__fileNames = []
		self.__lineNums = []
		#字典的值是列表，列表中保存文件绝对路径
		self.__typeAndFilenameDict = { 'py' : [], 'cpp' : [], 'c' : [], 'h' : [] }
		#字典的值是列表，列表中保存文件的行数，与self.__typeAndFilenameDict一一对应
		self.__typeAndNumsDict = { 'py' : [], 'cpp' : [], 'c' : [], 'h' : [] }
		'''
		if (timeStamp == "") :
			self.__timeStamp = 0
		else :
			self.__timeStamp = time.mktime(time.strptime(timeStamp, "%b-%d-%H:%M:%S-%Y"))
		'''
		self.__timeStamp = timeStamp
		self.__path = os.path.abspath(path)

	def __del__(self) :
		print "Count finished!"
	
	#检查命名合法性
	def __identifierChecker(self, str) :
		if (str[0] not in self.__alphas) :
			return False
		for otherChar in str[1:] :
			if (otherChar not in self.__alphasAndNums) :
				return False
		return True
	
	#计算python文件的行数
	def __getPyFileLines(self, fileName) :
		num = 0
		lineWithoutSpace = ""
		multLineComFlag = False
		strAssignFlag = False
		singleQuoMarkFlag = False#使用单引号注释多行--应对注释嵌套的情况
		doubleQuoMarkFlag = False#使用双引号注释多行--应对注释嵌套的情况
		triDQuo = '"' + '"' + '"'#即三引号"""
		triSQuo = "'" + "'" + "'"#即三引号'''
		strDoubleQuo = '=' + triDQuo#字符串赋值开始标识 ="""
		strSingleQuo = "=" + triSQuo#字符串赋值开始标识 ='''
		
		fh = open(fileName, "r")
		#前两行特殊处理
		line = fh.readline()
		#*nix系统中解释器说明行，处理UTF-8和UTF-8-BOM两种格式
		if ( (line[0:2] == '#!') or (line[3:5] == '#!') ) :
			num = 1
			line = fh.readline()
			if ( ("# -*-coding:UTF-8-*-" in line) or ("#coding=utf-8" in line) ) :
				num = 2
			else : #第二行未处理，文件指针回退，下面的for循环重新读取、处理
				fh.seek((0-len(line)), 1)
		elif ( ("# -*-coding:UTF-8-*-" in line) or ("#coding=utf-8" in line) ) :
			num = 1
		#第三行及往后的处理
		for line in fh.readlines():
			lineWithoutSpace = line.strip(' ').replace(' ', '').replace('\t', '')
			if (len(lineWithoutSpace) == 0) :
				continue
			#先前的多行注释已处理完
			if (multLineComFlag == False) :
				#空行、以#为首的单行注释行不计数
				if (lineWithoutSpace[0:2] == '\r\n' or lineWithoutSpace[0] == '\n' or lineWithoutSpace[0] == '#'):
					continue
				#是否使用三引号给字符串赋值
				elif ((strSingleQuo in lineWithoutSpace) or (strDoubleQuo in lineWithoutSpace)) :
					if( self.__identifierChecker(lineWithoutSpace[:lineWithoutSpace.find(strSingleQuo)])
					or  self.__identifierChecker(lineWithoutSpace[:lineWithoutSpace.find(strDoubleQuo)]) ) :
						strAssignFlag = True
						num += 1
				#行首遇到三引号：三引号给字符串赋值结束/同一行首末使用三引号注释/多行注释开始
				elif ((triSQuo == lineWithoutSpace[0:3]) or (triDQuo == lineWithoutSpace[0:3])) :
					#三引号赋值字符串结束--行首
					if (strAssignFlag == True) :
						strAssignFlag = False
						num += 1
					#同一行的首末使用三引号注释
					elif ( len(lineWithoutSpace) >= 6
					and (lineWithoutSpace[-4:] == (triSQuo + "\n") or lineWithoutSpace[-5:] == (triSQuo +"\r\n")) ) :
						continue
					elif ( len(lineWithoutSpace) >= 6
					and (lineWithoutSpace[-4:] == (triDQuo + '\n') or lineWithoutSpace[-5:] == (triDQuo + '\r\n')) ) :
						continue
					#多行注释开始
					else :
						multLineComFlag = True
						#使用单引号注释
						if (triSQuo == lineWithoutSpace[0:3]) :
							singleQuoMarkFlag = True
						#使用双引号注释
						elif (triDQuo == lineWithoutSpace[0:3]) :
							doubleQuoMarkFlag = True
				#行末遇到三引号：三引号赋值字符串结束，行末的三引号若用于注释只能是上面的那种情况（同一行注释）
				elif ( len(lineWithoutSpace) > 3
				and (lineWithoutSpace[-4:] == (triSQuo + "\n") or lineWithoutSpace[-5:] == (triSQuo +"\r\n")) ) :
					if (strAssignFlag == True) :
						strAssignFlag = False
						num += 1
				elif ( len(lineWithoutSpace) > 3
				and (lineWithoutSpace[-4:] == (triDQuo + "\n") or lineWithoutSpace[-5:] == (triDQuo +"\r\n")) ) :
					if (strAssignFlag == True) :
						strAssignFlag = False
						num += 1
				#正常的记入计数的行--除使用三引号给字符串赋值的行
				else :
					num += 1
			#多行注释内的处理
			else :
				#多行注释的代码块中包含三引号赋值字符串的语句
				if ((strSingleQuo in lineWithoutSpace) or (strDoubleQuo in lineWithoutSpace)) :
					strAssignFlag = True
				#多行注释代码块中三引号赋值是否结束/多行注注释结束
				elif ((triSQuo == lineWithoutSpace[0:3]) or (triDQuo == lineWithoutSpace[0:3])) :
					#三引号赋值
					if (strAssignFlag == True) :
						strAssignFlag = False
					#多行注释结束
					else :
						#单引号注释结束
						if (singleQuoMarkFlag == True) :
							singleQuoMarkFlag = False
							multLineComFlag = False
						#双引号注释结束
						elif (doubleQuoMarkFlag == True) :
							doubleQuoMarkFlag = False
							multLineComFlag = False
		fh.close()
		return num
	
	#计算C/C++文件的行数
	def __getCFileLines(self, fileName) :
		num = 0
		lineWithoutSpace = ""
		multLineComFlag = False
		starComFlag = False #使用/**/注释
		ifComFlag = False #使用#if 0 注释
		fh = open(fileName, "r")
		for line in fh.readlines() :
			lineWithoutSpace = line.strip(' ').replace(' ', '').replace('\t', '')
#			print lineWithoutSpace
			if (len(lineWithoutSpace) == 0) :
				continue
			#无多行注释
			if (multLineComFlag == False) :
				#空行、单行注释行不计数
				if (lineWithoutSpace[0:2] == '\r\n' or lineWithoutSpace[0] == '\n'
				or lineWithoutSpace[0:2] == '//'):
					continue
				elif ( ("/*" in lineWithoutSpace) or ("#if 0" in lineWithoutSpace) ):
					#同一行首末使用/**/注释或使用#if 0注释
					if ( ("*/" in lineWithoutSpace) or ("#endif" in lineWithoutSpace)) :
						continue
					#多行注释开始
					else :
						multLineComFlag = True
						if ("/*" in lineWithoutSpace) :
							starComFlag = True
						elif ("#if 0" in lineWithoutSpace) :
							ifComFlag = True
				else :
					num += 1
			#多行注释结束
			else :
				if ( ("*/" in lineWithoutSpace) or ("#endif" in lineWithoutSpace) ) :
					if (starComFlag == True) :
						starComFlag = False
						multLineComFlag = False
					elif (ifComFlag == True) :
						ifComFlag = False
						multLineComFlag = False
		fh.close()
		return num
	
	'''
	#根据文件类型选计算的函数
	def __getLineNumOfFile(self, fileName):
		num = 0
		nameAndExtension = fileName.split('.')
		#统计python文件的行数
		if (nameAndExtension[-1] == "py") :
			num = self.__getPyFileLines(fileName)
		#统计C/C++文件的行数
		elif ( (nameAndExtension[-1] == "cpp") or (nameAndExtension[-1] == "c")
		or (nameAndExtension[-1] == "h") ) :
			num = self.__getCFileLines(fileName)
		return num
	'''
	#递归遍历文件夹 找出python和C/C++文件
	def __traversalDir(self, path) :
		for fileName in os.listdir(path) :
			filePath = os.path.join(path, fileName)
			if os.path.isdir(filePath) :
				self.__traversalDir(filePath)
			else :
				if (' ' in fileName) : #文件名中有空格则不处理
					continue
				if (os.path.getctime(filePath) < self.__timeStamp) :
					continue
				extension = fileName.split('.')
				if (len(extension) < 2) :
					continue
				if (extension[-1] == "py") :
					self.__typeAndFilenameDict['py'].append(filePath)
				elif (extension[-1] == "cpp") : 
					self.__typeAndFilenameDict['cpp'].append(filePath)
				elif (extension[-1] == "c") :
					self.__typeAndFilenameDict['c'].append(filePath)
				elif (extension[-1] == "h") :
					self.__typeAndFilenameDict['h'].append(filePath)

	#测试打印
	def testP(self) :
		for fileName in self.__typeAndFilenameDict['py'] :
			print fileName
		for fileName in self.__typeAndFilenameDict['cpp'] :
			print fileName
		for fileName in self.__typeAndFilenameDict['c'] :
			print fileName	
		for fileName in self.__typeAndFilenameDict['h'] :
			print fileName

	#对外接口 返回文本行数
	def countLines(self) :
		self.__traversalDir(self.__path)
		for key, values in self.__typeAndFilenameDict.items() :
			for fileName in values :
				self.__typeAndNumsDict[key].append(self.__getPyFileLines(fileName))

	#对外接口 打印结果 结果加上时间戳追加到lines.txt文件中
	def couterPrint(self) :
		i = 0
		totallyNum = 0
		numDict = { 'py' : 0, 'cpp' : 0, 'c' : 0, 'h' : 0 }
		strResult = []

		strResult.append(time.strftime("%Y-%m-%d %H:%M", time.localtime()) + ":\n")
		if (self.__timeStamp > 0) :
			strResult.append("Files created after {0}:\n".
			format(time.strftime("%Y-%m-%d %H:%M", time.localtime(self.__timeStamp))))
		else :
			strResult.append("All Files:\n")
		for key, values in self.__typeAndFilenameDict.items() :
			for index in range(len(self.__typeAndFilenameDict[key])) :
				print ("%s,lineNums is %d" % (self.__typeAndFilenameDict[key][index],
				self.__typeAndNumsDict[key][index]))
				strResult.append("{0},lineNums is {1}\n".format(self.__typeAndFilenameDict[key][index],
				self.__typeAndNumsDict[key][index]))
				numDict[key] += self.__typeAndNumsDict[key][index]
			i += 1
			totallyNum += numDict[key]
		
		for key, values in numDict.items() :
			print ("LineNums of *.%s file is %d" % (key, values))
			strResult.append("LineNums of *.{0} file is {1}\n".format(key, values))		
		print ("Totally num is %d" % totallyNum)
#		print ("Residual task %d" % (100000-totallyNum))
		strResult.append("Totally num is {0}\n".format(totallyNum))
#		strResult.append("Residual task {0}\n\n".format(100000-totallyNum))
		with open("lines.txt", "a+") as fh :
			fh.writelines(strResult)
			fh.flush()
		fh.close()

def main() :
	'''
	if (len(sys.argv) == 3) :
		Lc = LinesCounter(sys.argv[1], sys.argv[2])
	elif (len(sys.argv) == 2) :
		Lc = LinesCounter(sys.argv[1], "")
	'''
	path = raw_input("please input dir of files: ")
	while(not os.path.isdir(path)) :
		path = raw_input("Your input is not a dir, please input again: ")
	timeStamp = raw_input("please input timeStamp: ")
	while(True) :
		if (timeStamp == 'ALL') :
			Lc = LinesCounter(path, 0)
			break
		else :
			try :
				sec = time.mktime(time.strptime(timeStamp, "%b-%d-%H:%M:%S-%Y"))
			except ValueError:
				#print "Wrong fomat of time"
				timeStamp = raw_input("Your input is invalid, please input again: ")
				continue
				#sec = time.mktime(time.strptime(timeStamp, "%b-%d-%H:%M:%S-%Y"))
			Lc = LinesCounter(path, sec)
			break
	Lc.countLines()
	Lc.couterPrint()

if __name__ == "__main__" :
	main()