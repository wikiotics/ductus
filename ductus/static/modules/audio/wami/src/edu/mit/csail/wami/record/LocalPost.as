package edu.mit.csail.wami.record
{	
	import edu.mit.csail.wami.utils.External;
	import edu.mit.csail.wami.utils.Pipe;
	import edu.mit.csail.wami.utils.StateListener;
	
	import flash.events.Event;
	import flash.events.HTTPStatusEvent;
	import flash.events.IOErrorEvent;
	import flash.events.ProgressEvent;
	import flash.events.SecurityErrorEvent;
	import flash.net.URLLoader;
	import flash.net.URLRequest;
	import flash.net.URLRequestMethod;
	import flash.utils.ByteArray;
	import flash.utils.setInterval;
	
	/**
	 * Store audio data locally on client side for recording/playback without exchanging with the server
	 */
	public class LocalPost extends Pipe
	{	
		private var url:String;
		private var contentType:String = null;
		private var listener:StateListener;

		private var finished:Boolean = false;
		private var buffer:ByteArray = new ByteArray();
		private var timeoutMillis:int;
		private var storage:ByteArray;		// the local storage of audio in localMode
		
		public function LocalPost(type:String, timeoutMillis:int, storage:ByteArray)
		{
			this.storage = storage;
			this.storage.position = 0;
			this.contentType = type;
			this.timeoutMillis = timeoutMillis;
		}
		
		override public function write(bytes:ByteArray):void
		{
			bytes.readBytes(buffer, buffer.length, bytes.bytesAvailable);
		}
		
		override public function close():void 
		{
			buffer.position = 0;
			
			if (buffer.bytesAvailable == 0) {
				External.debug("Note that flash does a GET request if bytes.length == 0");
			}

			try {
				buffer.readBytes(storage, 0, buffer.bytesAvailable);
				External.debug("Audio ("+ storage.length +" bytes) stored in local storage");
			} catch (error:Error) {
				External.debug("Error in LocalPost: " + error)
			}
			
			super.close();
		}
		
		private function completeHandler(event:Event):void {
			var loader:URLLoader = URLLoader(event.target);
			loader.removeEventListener(Event.COMPLETE, completeHandler);
			loader.removeEventListener(Event.OPEN, openHandler);
			loader.removeEventListener(ProgressEvent.PROGRESS, progressHandler);
			loader.removeEventListener(SecurityErrorEvent.SECURITY_ERROR, securityErrorHandler);
			loader.removeEventListener(HTTPStatusEvent.HTTP_STATUS, httpStatusHandler);
			loader.removeEventListener(IOErrorEvent.IO_ERROR, ioErrorHandler);
			finished = true;
		}
		
		private function openHandler(event:Event):void {
			setInterval(checkFinished, timeoutMillis);
		}
		
		private function checkFinished():void {
			if (!finished && listener) {
				listener.failed(new Error("POST is taking too long."));
			}
			finished = true;
		}
		
		private function progressHandler(event:ProgressEvent):void {
			External.debug("POST progressHandler loaded:" + event.bytesLoaded + " total: " + event.bytesTotal);
		}
		
		private function securityErrorHandler(event:SecurityErrorEvent):void {
			if (!finished && listener) 
			{
				listener.failed(new Error("Record security error: " + event.errorID));
			}
			finished = true;
		}
		
		private function httpStatusHandler(event:HTTPStatusEvent):void {
			if (!finished && listener && event.status != 200) 
			{
				listener.failed(new Error("HTTP status error: " + event.status));
			}
			finished = true;
		}
		
		private function ioErrorHandler(event:IOErrorEvent):void {
			if (!finished && listener) 
			{
				listener.failed(new Error("Record IO error: " + event.errorID));
			}
			finished = true;
		}
	}		
}
