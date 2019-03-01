/**************************** hmac.c ****************************/
/******************** See RFC 4634 for details ******************/
/*
 *  Description:
 *      This file implements the HMAC algorithm (Keyed-Hashing for
 *      Message Authentication, RFC2104), expressed in terms of the
 *      various SHA algorithms.
 */

#include <stdlib.h>
#include "sha.h"

#include "py/nlr.h"
#include "py/obj.h"
#include "py/runtime.h"
#include "py/binary.h"
#include "portmodules.h"

/*
 *  chmac_hmac
 *
 *  Description:
 *      This function transforms a query for HMAC from MicroPython
 *      into a query for C language.
 *
 *  Parameters:
 *      args[0]: [in]
 *          The secret shared key.
 *      args[1]: [in]
 *          The length of the secret shared key.
 *      args[2]: [in]
 *          An array of characters representing the message.
 *      args[3]: [in]
 *          The length of the message in message_array
 *
 *  Returns:
 *      the HMAC digest for given message and key.
 *
 */
STATIC mp_obj_t chmac_hmac(mp_uint_t n_args, const mp_obj_t *args)
{
    size_t key_len         = mp_obj_get_int(args[1]);
    const unsigned char* key  = (unsigned char*)(mp_obj_str_get_data(args[0], &key_len));
    const unsigned char* text = (unsigned char*)(mp_obj_str_get_str(args[2]));
    const size_t text_len        = mp_obj_get_int(args[3]);
    byte* digest = malloc(SHA256HashSize);
    hmac(SHA256, text, text_len, key, key_len, digest);
    return mp_obj_new_bytes(digest, SHA256HashSize);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(chmac_hmac_obj, 4, 4, chmac_hmac);

STATIC const mp_map_elem_t chmac_globals_table[] = {
    { MP_OBJ_NEW_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_chmac) },
    { MP_OBJ_NEW_QSTR(MP_QSTR_hmac), (mp_obj_t)&chmac_hmac_obj },
};

STATIC MP_DEFINE_CONST_DICT (
    mp_module_chmac_globals,
    chmac_globals_table
);

const mp_obj_module_t mp_module_chmac = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&mp_module_chmac_globals,
};


/*
 *  hmac
 *
 *  Description:
 *      This function will compute an HMAC message digest.
 *
 *  Parameters:
 *      whichSha: [in]
 *          One of SHA1, SHA224, SHA256, SHA384, SHA512
 *      key: [in]
 *          The secret shared key.
 *      key_len: [in]
 *          The length of the secret shared key.
 *      message_array: [in]
 *          An array of characters representing the message.
 *      length: [in]
 *          The length of the message in message_array
 *      digest: [out]
 *          Where the digest is returned.
 *          NOTE: The length of the digest is determined by
 *              the value of whichSha.
 *
 *  Returns:
 *      sha Error Code.
 *
 */
int
hmac (SHAversion whichSha, const unsigned char *text, int text_len,
      const unsigned char *key, int key_len, uint8_t digest[USHAMaxHashSize])
{
  HMACContext ctx;
  return hmacReset (&ctx, whichSha, key, key_len) ||
    hmacInput (&ctx, text, text_len) || hmacResult (&ctx, digest);
}

/*
 *  hmacReset
 *
 *  Description:
 *      This function will initialize the hmacContext in preparation
 *      for computing a new HMAC message digest.
 *
 *  Parameters:
 *      context: [in/out]
 *          The context to reset.
 *      whichSha: [in]
 *          One of SHA1, SHA224, SHA256, SHA384, SHA512
 *      key: [in]
 *          The  secret shared key.
 *      key_len: [in]
 *          The length of the secret shared key.
 *
 *  Returns:
 *      sha Error Code.
 *
 */
int
hmacReset (HMACContext * ctx, enum SHAversion whichSha,
	   const unsigned char *key, int key_len)
{
  int i, blocksize, hashsize;

  /* inner padding - key XORd with ipad */
  unsigned char k_ipad[USHA_Max_Message_Block_Size];

  /* temporary buffer when keylen > blocksize */
  unsigned char tempkey[USHAMaxHashSize];

  if (!ctx)
    return shaNull;

  blocksize = ctx->blockSize = USHABlockSize (whichSha);
  hashsize = ctx->hashSize = USHAHashSize (whichSha);

  ctx->whichSha = whichSha;

  /*
   * If key is longer than the hash blocksize,
   * reset it to key = HASH(key).
   */
  if (key_len > blocksize)
    {
      USHAContext tctx;
      int err = USHAReset (&tctx, whichSha) ||
	USHAInput (&tctx, key, key_len) || USHAResult (&tctx, tempkey);
      if (err != shaSuccess)
	return err;

      key = tempkey;
      key_len = hashsize;
    }

  /*
   * The HMAC transform looks like:
   *
   * SHA(K XOR opad, SHA(K XOR ipad, text))
   *
   * where K is an n byte key.
   * ipad is the byte 0x36 repeated blocksize times
   * opad is the byte 0x5c repeated blocksize times
   * and text is the data being protected.
   */

  /* store key into the pads, XOR'd with ipad and opad values */
  for (i = 0; i < key_len; i++)
    {
      k_ipad[i] = key[i] ^ 0x36;
      ctx->k_opad[i] = key[i] ^ 0x5c;
    }
  /* remaining pad bytes are '\0' XOR'd with ipad and opad values */
  for (; i < blocksize; i++)
    {
      k_ipad[i] = 0x36;
      ctx->k_opad[i] = 0x5c;
    }

  /* perform inner hash */
  /* init context for 1st pass */
  return USHAReset (&ctx->shaContext, whichSha) ||
    /* and start with inner pad */
    USHAInput (&ctx->shaContext, k_ipad, blocksize);
}

/*
 *  hmacInput
 *
 *  Description:
 *      This function accepts an array of octets as the next portion
 *      of the message.
 *
 *  Parameters:
 *      context: [in/out]
 *          The HMAC context to update
 *      message_array: [in]
 *          An array of characters representing the next portion of
 *          the message.
 *      length: [in]
 *          The length of the message in message_array
 *
 *  Returns:
 *      sha Error Code.
 *
 */
int
hmacInput (HMACContext * ctx, const unsigned char *text, int text_len)
{
  if (!ctx)
    return shaNull;
  /* then text of datagram */
  return USHAInput (&ctx->shaContext, text, text_len);
}

/*
 * HMACFinalBits
 *
 * Description:
 *   This function will add in any final bits of the message.
 *
 * Parameters:
 *   context: [in/out]
 *     The HMAC context to update
 *   message_bits: [in]
 *     The final bits of the message, in the upper portion of the
 *     byte. (Use 0b###00000 instead of 0b00000### to input the
 *     three bits ###.)
 *   length: [in]
 *     The number of bits in message_bits, between 1 and 7.
 *
 * Returns:
 *   sha Error Code.
 */
int
hmacFinalBits (HMACContext * ctx, const uint8_t bits, unsigned int bitcount)
{
  if (!ctx)
    return shaNull;
  /* then final bits of datagram */
  return USHAFinalBits (&ctx->shaContext, bits, bitcount);
}

/*
 * HMACResult
 *
 * Description:
 *   This function will return the N-byte message digest into the
 *   Message_Digest array provided by the caller.
 *   NOTE: The first octet of hash is stored in the 0th element,
 *      the last octet of hash in the Nth element.
 *
 * Parameters:
 *   context: [in/out]
 *     The context to use to calculate the HMAC hash.
 *   digest: [out]
 *     Where the digest is returned.
 *   NOTE 2: The length of the hash is determined by the value of
 *      whichSha that was passed to hmacReset().
 *
 * Returns:
 *   sha Error Code.
 *
 */
int
hmacResult (HMACContext * ctx, uint8_t * digest)
{
  if (!ctx)
    return shaNull;

  /* finish up 1st pass */
  /* (Use digest here as a temporary buffer.) */
  return USHAResult (&ctx->shaContext, digest) ||
    /* perform outer SHA */
    /* init context for 2nd pass */
    USHAReset (&ctx->shaContext, ctx->whichSha) ||
    /* start with outer pad */
    USHAInput (&ctx->shaContext, ctx->k_opad, ctx->blockSize) ||
    /* then results of 1st hash */
    USHAInput (&ctx->shaContext, digest, ctx->hashSize) ||
    /* finish up 2nd pass */
    USHAResult (&ctx->shaContext, digest);
}
