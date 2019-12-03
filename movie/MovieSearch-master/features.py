# sort output by selected attribute and return
def sort_by(output, attribute = 'title', direction = False):
        if(attribute != 'title'):
                direction = True
        output = sorted(output, key = lambda x:x[attribute], 
                reverse = direction)
        return output

# filter by some attribute, build new output list and return
def filter_by(output, attribute, low, high):
        filtered_output = []
        if(low == ''):
                low = 0
        if(high == ''):
                high = 10000

        for movie in output:
                if( movie[attribute] >= int(low) and movie[attribute] <= int(high) ):
                        # if( movie['score'] >= score_low and movie['score'] <= score_high ):
                        #         if( movie['runtime'] >= runtime_low and movie['runtime'] <= runtime_high ):
                        filtered_output.append(movie)

        return filtered_output
