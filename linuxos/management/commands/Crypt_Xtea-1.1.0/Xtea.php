<?php
/* vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4: */
//
// +----------------------------------------------------------------------+
// | PHP version 4.0                                                      |
// +----------------------------------------------------------------------+
// | Copyright (c) 2002-2004 The PHP Group                                |
// +----------------------------------------------------------------------+
// | This source file is subject to version 2.02 of the PHP license,      |
// | that is bundled with this package in the file LICENSE, and is        |
// | available at through the world-wide-web at                           |
// | http://www.php.net/license/2_02.txt.                                 |
// | If you did not receive a copy of the PHP license and are unable to   |
// | obtain it through the world-wide-web, please send a note to          |
// | license@php.net so we can mail you a copy immediately.               |
// +----------------------------------------------------------------------+
// | Authors: Jeroen Derks <jeroen@derks.it>                              |
// +----------------------------------------------------------------------+
// | Original code: http://vader.brad.ac.uk/tea/source.shtml#new_ansi     |
// | Currently to be found at:                                            |
// | http://www.simonshepherd.supanet.com/source.shtml#new_ansi           |
// +----------------------------------------------------------------------+
//
// $Id: Xtea.php,v 1.14 2008/03/06 20:01:56 jeroend Exp $
//

/** PEAR base class */
require_once 'PEAR.php';

/**
 *  Class that implements the xTEA encryption algorithm.
 *  Class that implements the xTEA encryption algorithm.<br />
 *  This enables you to encrypt data without requiring mcrypt.
 *
 *  From the C source:
 *  -----------------------------------------
 *  The Tiny Encryption Algorithm (TEA) by
 *  David Wheeler and Roger Needham of the
 *  Cambridge Computer Laboratory.
 *
 *  Placed in the Public Domain by
 *  David Wheeler and Roger Needham.
 *
 *  **** ANSI C VERSION (New Variant) ****
 *
 *  Notes:
 *
 *  TEA is a Feistel cipher with XOR and
 *  and addition as the non-linear mixing
 *  functions.
 *
 *  Takes 64 bits of data in v[0] and v[1].
 *  Returns 64 bits of data in w[0] and w[1].
 *  Takes 128 bits of key in k[0] - k[3].
 *
 *  TEA can be operated in any of the modes
 *  of DES. Cipher Block Chaining is, for example,
 *  simple to implement.
 *
 *  n is the number of iterations. 32 is ample,
 *  16 is sufficient, as few as eight may be OK.
 *  The algorithm achieves good dispersion after
 *  six iterations. The iteration count can be
 *  made variable if required.
 *
 *  Note this is optimised for 32-bit CPUs with
 *  fast shift capabilities. It can very easily
 *  be ported to assembly language on most CPUs.
 *
 *  delta is chosen to be the real part of (the
 *  golden ratio Sqrt(5/4) - 1/2 ~ 0.618034
 *  multiplied by 2^32).
 *
 *  This version has been amended to foil two
 *  weaknesses identified by David A. Wagner
 *  (daw@cs.berkeley.edu): 1) effective key
 *  length of old-variant TEA was 126 not 128
 *  bits 2) a related key attack was possible
 *  although impractical.
 *
 *  void encipher(unsigned long *const v,unsigned long *const w,
 *  const unsigned long *const k)
 *  {
 *   register unsigned long       y=v[0],z=v[1],sum=0,delta=0x9E3779B9,n=32;
 *
 *   while(n-->0)
 *      {
 *        y+= (z<<4 ^ z>>5) + z ^ sum + k[sum&3];
 *      sum += delta;
 *      z+= (y<<4 ^ y>>5) + y ^ sum + k[sum>>11 & 3];
 *      }
 *
 *   w[0]=y; w[1]=z;
 *  }
 *
 *  void decipher(unsigned long *const v,unsigned long *const w,
 *  const unsigned long *const k)
 *  {
 *   register unsigned long       y=v[0],z=v[1],sum=0xC6EF3720,
 *                                delta=0x9E3779B9,n=32;
 *
 *   # sum = delta<<5, in general sum = delta * n
 *
 *       while(n-->0)
 *          {
 *            z-= (y<<4 ^ y>>5) + y ^ sum + k[sum>>11 & 3];
 *          sum -= delta;
 *            y-= (z<<4 ^ z>>5) + z ^ sum + k[sum&3];
 *          }
 *
 *   w[0]=y; w[1]=z;
 *  }
 *
 *  -----------------------------------------
 *
 *  @TODO       Add CFB.
 *
 *  @package    Crypt_Xtea
 *  @version    $Revision: 1.14 $
 *  @access     public
 *  @author     Jeroen Derks <jeroen@derks.it>
 */

class Crypt_Xtea extends PEAR
{

    /**
     *  Number of iterations.
     *  @var    integer
     *  @access private
     *  @see    setIter(), getIter()
     */
    var $n_iter;


    // {{{ Crypt_Xtea()

    /**
     *  Constructor, sets the number of iterations.
     *
     *  @access public
     *  @author         Jeroen Derks <jeroen@derks.it>
     *  @see            setIter()
     */
    function Crypt_Xtea()
    {
        $this->setIter(32);
    }

    // }}}
    // {{{ setIter()

    /**
     *  Set the number of iterations to use.
     *
     *  @param  integer $n_iter Number of iterations to use.
     *
     *  @access public
     *  @author         Jeroen Derks <jeroen@derks.it>
     *  @see            $n_iter, getIter()
     */
    function setIter($n_iter)
    {
        $this->n_iter = $n_iter;
    }

    // }}}
    // {{{ getIter()

    /**
     *  Get the number of iterations to use.
     *
     *  @return integer Number of iterations to use.
     *
     *  @access public
     *  @author         Jeroen Derks <jeroen@derks.it>
     *  @see            $n_iter, setIter()
     */
    function getIter()
    {
        return $this->n_iter;
    }

    // }}}
    // {{{ encrypt()

    /**
     *  Encrypt a string using a specific key.
     *
     *  @param  string  $data   Data to encrypt.
     *  @param  string  $key    Key to encrypt data with (binary string).
     *
     *  @return string          Binary encrypted character string.
     *
     *  @access public
     *  @author         Jeroen Derks <jeroen@derks.it>
     *  @see            decrypt(), _encipherLong(), _resize(), _str2long()
     */
    function encrypt($data, $key)
    {
        // resize data to 32 bits (4 bytes)
        $n = $this->_resize($data, 4);

        // convert data to long
        $data_long[0]   = $n;
        $n_data_long    = $this->_str2long(1, $data, $data_long);

        // resize data_long to 64 bits (2 longs of 32 bits)
        $n = count($data_long);
        if (($n & 1) == 1) {
            $data_long[$n] = chr(0);
            $n_data_long++;
        }

        // resize key to a multiple of 128 bits (16 bytes)
        $this->_resize($key, 16, true);
        if ( '' == $key )
            $key = '0000000000000000';

        // convert key to long
        $n_key_long = $this->_str2long(0, $key, $key_long);

        // encrypt the long data with the key
        $enc_data   = '';
        $w          = array(0, 0);
        $j          = 0;
        $k          = array(0, 0, 0, 0);
        for ($i = 0; $i < $n_data_long; ++$i) {
            // get next key part of 128 bits
            if ($j + 4 <= $n_key_long) {
                $k[0] = $key_long[$j];
                $k[1] = $key_long[$j + 1];
                $k[2] = $key_long[$j + 2];
                $k[3] = $key_long[$j + 3];
            } else {
                $k[0] = $key_long[$j % $n_key_long];
                $k[1] = $key_long[($j + 1) % $n_key_long];
                $k[2] = $key_long[($j + 2) % $n_key_long];
                $k[3] = $key_long[($j + 3) % $n_key_long];
            }
            $j = ($j + 4) % $n_key_long;

            $this->_encipherLong($data_long[$i], $data_long[++$i], $w, $k);

            // append the enciphered longs to the result
            $enc_data .= $this->_long2str($w[0]);
            $enc_data .= $this->_long2str($w[1]);
        }

        return $enc_data;
    }

    // }}}
    // {{{ decrypt()

    /**
     *  Decrypt an encrypted string using a specific key.
     *
     *  @param  string  $data   Encrypted data to decrypt.
     *  @param  string  $key    Key to decrypt encrypted data with (binary string).
     *
     *  @return string          Binary decrypted character string.
     *
     *  @access public
     *  @author         Jeroen Derks <jeroen@derks.it>
     *  @see            _encipherLong(), encrypt(), _resize(), _str2long()
     */
    function decrypt($enc_data, $key)
    {
        // convert data to long
        $n_enc_data_long = $this->_str2long(0, $enc_data, $enc_data_long);

        // resize key to a multiple of 128 bits (16 bytes)
        $this->_resize($key, 16, true);
        if ( '' == $key )
            $key = '0000000000000000';

        // convert key to long
        $n_key_long = $this->_str2long(0, $key, $key_long);

        // decrypt the long data with the key
        $data   = '';
        $w      = array(0, 0);
        $j      = 0;
        $len    = 0;
        $k      = array(0, 0, 0, 0);
        $pos    = 0;

        for ($i = 0; $i < $n_enc_data_long; $i += 2) {
            // get next key part of 128 bits
            if ($j + 4 <= $n_key_long) {
                $k[0] = $key_long[$j];
                $k[1] = $key_long[$j + 1];
                $k[2] = $key_long[$j + 2];
                $k[3] = $key_long[$j + 3];
            } else {
                $k[0] = $key_long[$j % $n_key_long];
                $k[1] = $key_long[($j + 1) % $n_key_long];
                $k[2] = $key_long[($j + 2) % $n_key_long];
                $k[3] = $key_long[($j + 3) % $n_key_long];
            }
            $j = ($j + 4) % $n_key_long;

            $this->_decipherLong($enc_data_long[$i], $enc_data_long[$i + 1], $w, $k);
 
            // append the deciphered longs to the result data (remove padding)
            if (0 == $i) {
                $len = $w[0];
                if (4 <= $len) {
                    $data .= $this->_long2str($w[1]);
                } else {
                    $data .= substr($this->_long2str($w[1]), 0, $len % 4);
                }
            } else {
                $pos = ($i - 1) * 4;
                if ($pos + 4 <= $len) {
                    $data .= $this->_long2str($w[0]);

                    if ($pos + 8 <= $len) {
                        $data .= $this->_long2str($w[1]);
                    } elseif ($pos + 4 < $len) {
                        $data .= substr($this->_long2str($w[1]), 0, $len % 4);
                    }
                } else {
                    $data .= substr($this->_long2str($w[0]), 0, $len % 4);
                }
            }
        }
        return $data;
    }

    // }}}
    // {{{ _encipherLong()

    /**
     *  Encipher a single long (32-bit) value.
     *
     *  @param  integer $y  32 bits of data.
     *  @param  integer $z  32 bits of data.
     *  @param  array   &$w Placeholder for enciphered 64 bits (in w[0] and w[1]).
     *  @param  array   &$k Key 128 bits (in k[0]-k[3]).
     *
     *  @access private
     *  @author         Jeroen Derks <jeroen@derks.it>
     *  @see            $n_iter, _add(), _rshift(), _decipherLong()
     */
    function _encipherLong($y, $z, &$w, &$k)
    {
        $sum    = (integer) 0;
        $delta  = 0x9E3779B9;
        $n      = (integer) $this->n_iter;

        while ($n-- > 0) {
            $y      = $this->_add($y,
                                  $this->_add($z << 4 ^ $this->_rshift($z, 5), $z) ^
                                    $this->_add($sum, $k[$sum & 3]));
            $sum    = $this->_add($sum, $delta);
            $z      = $this->_add($z,
                                  $this->_add($y << 4 ^ $this->_rshift($y, 5), $y) ^
                                    $this->_add($sum, $k[$this->_rshift($sum, 11) & 3]));
        }

        $w[0] = $y;
        $w[1] = $z;
    }

    // }}}
    // {{{ _decipherLong()

    /**
     *  Decipher a single long (32-bit) value.
     *
     *  @param  integer $y  32 bits of enciphered data.
     *  @param  integer $z  32 bits of enciphered data.
     *  @param  array   &$w Placeholder for deciphered 64 bits (in w[0] and w[1]).
     *  @param  array   &$k Key 128 bits (in k[0]-k[3]).
     *
     *  @access private
     *  @author         Jeroen Derks <jeroen@derks.it>
     *  @see            $n_iter, _add(), _rshift(), _decipherLong()
     */
    function _decipherLong($y, $z, &$w, &$k)
    {
        // sum = delta<<5, in general sum = delta * n
        $sum    = 0xC6EF3720;
        $delta  = 0x9E3779B9;
        $n      = (integer) $this->n_iter;

        while ($n-- > 0) {
            $z      = $this->_add($z,
                                  -($this->_add($y << 4 ^ $this->_rshift($y, 5), $y) ^
                                        $this->_add($sum, $k[$this->_rshift($sum, 11) & 3])));
            $sum    = $this->_add($sum, -$delta);
            $y      = $this->_add($y,
                                  -($this->_add($z << 4 ^ $this->_rshift($z, 5), $z) ^
                                        $this->_add($sum, $k[$sum & 3])));
        }

        $w[0] = $y;
        $w[1] = $z;
    }

    // }}}
    // {{{ _resize()

    /**
     *  Resize data string to a multiple of specified size.
     *
     *  @param  string  $data   Data string to resize to specified size.
     *  @param  integer $size   Size in bytes to align data to.
     *  @param  boolean $nonull Set to true if padded bytes should not be zero.
     *
     *  @return integer         Length of supplied data string.
     *
     *  @access private
     *  @author         Jeroen Derks <jeroen@derks.it>
     */
    function _resize(&$data, $size, $nonull = false)
    {
        $n      = strlen($data);
        $nmod   = $n % $size;
        if ( 0 == $nmod )
            $nmod = $size;

        if ($nmod > 0) {
            if ($nonull) {
                for ($i = $n; $i < $n - $nmod + $size; ++$i) {
                    $data[$i] = $data[$i % $n];
                }
            } else {
                for ($i = $n; $i < $n - $nmod + $size; ++$i) {
                    $data[$i] = chr(0);
                }
            }
        }
        return $n;
    }

    // }}}
    // {{{ _hex2bin()

    /**
     *  Convert a hexadecimal string to a binary string (e.g. convert "616263" to "abc").
     *
     *  @param  string  $str    Hexadecimal string to convert to binary string.
     *
     *  @return string          Binary string.
     *
     *  @access private
     *  @author         Jeroen Derks <jeroen@derks.it>
     */
    function _hex2bin($str)
    {
        $len = strlen($str);
        return pack('H' . $len, $str);
    }

    // }}}
    // {{{ _str2long()

    /**
     *  Convert string to array of long.
     *
     *  @param  integer $start      Index into $data_long for output.
     *  @param  string  &$data      Input string.
     *  @param  array   &$data_long Output array of long.
     *
     *  @return integer             Index from which to optionally continue.
     *
     *  @access private
     *  @author         Jeroen Derks <jeroen@derks.it>
     */
    function _str2long($start, &$data, &$data_long)
    {
        $n = strlen($data);

        $tmp    = unpack('N*', $data);
        $j      = $start;

        foreach ($tmp as $value)
            $data_long[$j++] = $value;

        return $j;
    }

    // }}}
    // {{{ _long2str()

    /**
     *  Convert long to character string.
     *
     *  @param  long    $l  Long to convert to character string.
     *
     *  @return string      Character string.
     *
     *  @access private
     *  @author         Jeroen Derks <jeroen@derks.it>
     */
    function _long2str($l)
    {
        return pack('N', $l);
    }

    // }}}
    // {{{ _rshift()
    
    /**
     *  Handle proper unsigned right shift, dealing with PHP's signed shift.
     *
     *  @access private
     *  @since          2004/Sep/06
     *  @author         Jeroen Derks <jeroen@derks.it>
     */
    function _rshift($integer, $n)
    {
        // convert to 32 bits
        if (0xffffffff < $integer || -0xffffffff > $integer) {
            $integer = fmod($integer, 0xffffffff + 1);
        }

        // convert to unsigned integer
        if (0x7fffffff < $integer) {
            $integer -= 0xffffffff + 1.0;
        } elseif (-0x80000000 > $integer) {
            $integer += 0xffffffff + 1.0;
        }

        // do right shift
        if (0 > $integer) {
            $integer &= 0x7fffffff;                     // remove sign bit before shift
            $integer >>= $n;                            // right shift
            $integer |= 1 << (31 - $n);                 // set shifted sign bit
        } else {
            $integer >>= $n;                            // use normal right shift
        }

        return $integer;
    }

    // }}}
    // {{{ _add()
    
    /**
     *  Handle proper unsigned add, dealing with PHP's signed add.
     *
     *  @access private
     *  @since          2004/Sep/06
     *  @author         Jeroen Derks <jeroen@derks.it>
     */
    function _add($i1, $i2)
    {
        $result = 0.0;

        foreach (func_get_args() as $value) {
            // remove sign if necessary
            if (0.0 > $value) {
                $value -= 1.0 + 0xffffffff;
            }

            $result += $value;
        }

        // convert to 32 bits
        if (0xffffffff < $result || -0xffffffff > $result) {
            $result = fmod($result, 0xffffffff + 1);
        }

        // convert to signed integer
        if (0x7fffffff < $result) {
            $result -= 0xffffffff + 1.0;
        } elseif (-0x80000000 > $result) {
            $result += 0xffffffff + 1.0;
        }

        return $result;
    }

    // }}}
}

?>
