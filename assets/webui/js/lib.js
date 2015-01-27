/*
 *  This file is part of AminoPVR.
 *  Copyright (C) 2012  Ino Dekker
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

Date.prototype._getMonthHuman = function()
{
    var months = [ "January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December" ];
    return months[this.getMonth()];
}

Date.prototype._getDayHuman = function()
{
    var days = [ "Sunday", "Monday", "Thusday", "Wednesday", "Thursday", "Friday", "Saturday" ];
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

if ( typeof String.prototype.startsWith != 'function' )
{
    String.prototype.startsWith = function( str )
    {
        return this.slice( 0, str.length ) == str;
    };
}

if ( typeof String.prototype.endsWith != 'function' )
{
    String.prototype.endsWith = function( str )
    {
        return this.slice( -str.length ) == str;
    };
}
