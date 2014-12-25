Date.prototype._getMonthHuman = function()
{
    var months = [ "January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December" ];
    return months[this.getMonth()];
}

Date.prototype._getDayHuman = function()
{
    var days = [ "Monday", "Thusday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday" ];
    return days[this.getDay()];
}

Date.prototype._toHuman = function()
{
    return this._getDayHuman() + ", " + this._getMonthHuman() + " " + this.getDate() + ", " + this.getFullYear() + ", " + this._toHHMM();
}

Date.prototype._toHHMM = function()
{
    var hours   = this.getHours();
    var minutes = this.getMinutes();

    if (hours   < 10) {hours   = "0"+hours;}
    if (minutes < 10) {minutes = "0"+minutes;}
    var time    = hours+':'+minutes;
    return time;
}

Date.prototype._toLocalJSON = function()
{
    return this.getFullYear() + "-" + zeroPadded( this.getMonth() + 1 ) + "-" + zeroPadded( this.getDate() ) + "T" + zeroPadded( this.getHours() ) + ":" + zeroPadded( this.getMinutes() ) + ":" + zeroPadded( this.getSeconds() );
}

Date.prototype._toUTC = function()
{
    return new Date( this._getUTCTime() );
}

Date.prototype._getUTCTime = function()
{
    return this.getTime() + (this.getTimezoneOffset() * 60000);
}

function zeroPadded( val )
{
    if ( val >= 10 )
        return val;
    else
        return '0' + val;
}

function roundTo15Minutes( timestamp )
{
    return timestamp - (timestamp % (15 * 60));
}
