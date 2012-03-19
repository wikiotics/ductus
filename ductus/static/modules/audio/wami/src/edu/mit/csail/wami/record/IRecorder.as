/* 
* Copyright (c) 2011
* Spoken Language Systems Group
* MIT Computer Science and Artificial Intelligence Laboratory
* Massachusetts Institute of Technology
*
* Permission is hereby granted, free of charge, to any person
* obtaining a copy of this software and associated documentation
* files (the "Software"), to deal in the Software without
* restriction, including without limitation the rights to use, copy,
* modify, merge, publish, distribute, sublicense, and/or sell copies
* of the Software, and to permit persons to whom the Software is
* furnished to do so, subject to the following conditions:
*
* The above copyright notice and this permission notice shall be
* included in all copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
* EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
* MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
* NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
* BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
* ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
* CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
* SOFTWARE.
*/
package edu.mit.csail.wami.record
{
	import edu.mit.csail.wami.utils.StateListener;
	import flash.utils.ByteArray;

	public interface IRecorder
	{
		// Start and stop recording.  Calling start while recording
		// or calling stop when not recording should have no effect.
		function start(url:String, listener:StateListener):void; 
		function stop():void;
		
		// It can be helpful to buffer a certain amount of audio to 
		// prepend (and append) to the audio collected between start
		// and stop.  This means, Flash needs to constantly listen.
		// There are other times when it's obvious no recording will
		// be done, and so listening is unnecesary.
		function listen(paddingMillis:uint):void;
		function unlisten():void;
		
		// Audio level (between 0 and 100)
		function level():int; 

		// must be called before start to set local variables, or the
		// recorder will be in an unknown state
		function setLocalStorage(storage:ByteArray):void
	}
}
