import operator, math, sys

QREL_PATH_HW1 = '/Users/xinshu/desktop/CS6200/DATA/AP_DATA/qrels.adhoc.51-100.AP89.txt'
RANK_PATH_HW1 = '/Users/xinshu/desktop/CS6200/Assignments/HW1/results/bm25'

QREL_PATH_HW5 = '/Users/xinshu/desktop/CS6200/Assignments/HW5/data/qrel.txt'
RANK_PATH_HW5 = '/Users/xinshu/desktop/CS6200/Assignments/HW5/data/rank.txt'

OUTPATH = '/Users/xinshu/desktop/CS6200/Assignments/HW5/results/'

class TrecEval:
    def __init__(self, qrel, rank, output_all):
        self.output = output_all
        self.qrel, self.rel = self.get_qrel_dict(qrel)
        self.rank = self.get_rank_dict(rank)
        self.recalls = self.get_recalls()
        self.cutoffs = [5,10,20,50,100]

        self.avg_precision_map = {}
        self.r_precision_map = {}
        self.ndcg_map = {}

        self.max = 1000
        self.sum_prec_at_cutoff = [0 for i in range(len(self.cutoffs))]
        self.sum_rec_at_cutoff = [0 for i in range(len(self.cutoffs))]
        self.sum_f_at_cutoff = [0 for i in range(len(self.cutoffs))]


    def get_qrel_dict(self, qrelfile):
        fh = open(qrelfile, "r")
        qrel_dict = {}

        for line in fh.readlines():
            query_id, _, doc_id, grade = line.split()
            grade = int(grade)
            
            if grade != 0:
                if query_id not in qrel_dict:
                    qrel_dict[query_id] = {doc_id: grade}
                else:
                    qrel_dict[query_id][doc_id] = grade
                    
        rel_dict = {}
        for key in sorted(qrel_dict.keys()):
            print "The qrel", key, "has", len(qrel_dict[key])
            rel_dict[key] = len(qrel_dict[key])
        fh.close()
        return qrel_dict, rel_dict

    def get_rank_dict(self, rankfile):
        fh = open(rankfile, "r")
        rank_dict = {}

        for line in fh.readlines():
            query_id, _, doc_id, rank, _, _ = line.split()

            if query_id not in rank_dict:
                rank = int(rank)
                rank_dict[query_id] = {rank: doc_id}
            else:
                rank_dict[query_id][rank] = doc_id
                
        for key in rank_dict:
            print "The rank", key, "has", len(rank_dict[key])
        fh.close()
        return rank_dict

    def get_recalls(self):
        recalls = [round(x * 0.01,3) for x in range(100*0, 100*1 + 1)]
        print 'recalls: ', recalls
        return recalls

    def trec_models(self):
        tot_num_ret = 0
        tot_num_rel = 0
        tot_num_rel_ret = 0
        
        for query in sorted(self.rank.keys()):
            if query not in self.rel:
                continue
            
            rq = self.rel[query]
            tot_num_rel += rq
            href = self.rank[query]
            prec_list = [0] * (self.max + 1)
            rec_list = [0] * (self.max + 1)

            num_ret = 0
            num_rel_ret = 0
            sum_prec = 0
            sum_dcg = 0
            rel_ret = []

            # calculate sum_prec and sum_dcg
            for rank in sorted(href.keys(), key=int):
                num_ret += 1
                doc_id = href[rank]

                if doc_id in self.qrel[query]:

                    num_rel_ret += 1
                    sum_prec += float(num_rel_ret) / num_ret
                
                    grade = self.qrel[query][doc_id]
                    
                    if num_ret == 1:
                        sum_dcg = float(2 ** grade -1)
                    else:
                        sum_dcg += float(2 ** grade -1) / math.log(num_ret)

                    rel_ret.append(grade)

                prec_list[num_ret] = float(num_rel_ret) / num_ret
                rec_list[num_ret] = float(num_rel_ret) / rq

                if num_ret >= self.max:
                    break

            # calculate average precision
            avg_prec = sum_prec / rq
            self.avg_precision_map[query] = avg_prec

            # calculate ndcg
            idcg = self.get_idcg(rel_ret)
            ndcg = sum_dcg / idcg
            self.ndcg_map[query] = ndcg

            final_recall = num_rel_ret / rq

            # fill out the rest of precision/recall lists
            if num_ret < self.max:
                for i in range(num_ret + 1, self.max):
                    prec_list[i] = float(num_rel_ret) / i
                    rec_list[i] = final_recall

            # calculate precision/recall/f @k
            prec_at_cutoff, rec_at_cutoff, f_at_cutoff= self.get_prec_recall_f_at_cutoff(prec_list, rec_list)

            # calculate r-precision
            r_prec = self.calculate_r_precision(query, rq, num_ret,
                                                num_rel_ret, prec_list)

            # calculate interpolated precisions
            prec_inter_list = list(prec_list)
            max_prec = 0
            for i in range(len(prec_inter_list)-1, -1, -1):
                if prec_inter_list[i] > max_prec:
                    max_prec = prec_inter_list[i]
                else:
                    prec_inter_list[i] = max_prec

            self.write_prec_recall_file(query, rec_list, prec_inter_list)


            if self.output:
                self.print_to_screen(int(query), num_ret, rq, num_rel_ret,
                                     r_prec, avg_prec, ndcg, prec_at_cutoff,
                                     rec_at_cutoff, f_at_cutoff)
                
            tot_num_ret += num_ret
            print tot_num_ret
            tot_num_rel_ret += num_rel_ret
            
        self.print_all(tot_num_ret, tot_num_rel_ret, tot_num_rel)

    def get_idcg(self,rel_ret):
        sorted_rel_ret = sorted(rel_ret, reverse=True)
        idcg = 0.0
        for i in range(len(sorted_rel_ret)):
            if i == 0:
                idcg += sorted_rel_ret[i]
            else:
                idcg += float(2 ** sorted_rel_ret[i] - 1) / math.log(i + 1)
        return idcg

    def get_prec_recall_f_at_cutoff(self, prec_list, rec_list):
        prec_at_cutoff = []
        rec_at_cutoff = []
        f_at_cutoff = []
        
        for i in self.cutoffs:
            prec = prec_list[i]
            recall = rec_list[i]
            prec_at_cutoff.append(prec)
            rec_at_cutoff.append(recall)
            
            if prec or recall:
                f_measure = 2 * prec * recall / (prec + recall)
                f_at_cutoff.append(f_measure)
            else:
                f_at_cutoff.append(0)
        
        for i in range(len(self.cutoffs)):
            self.sum_prec_at_cutoff[i] += prec_at_cutoff[i]
            self.sum_rec_at_cutoff[i] += rec_at_cutoff[i]
            self.sum_f_at_cutoff[i] += f_at_cutoff[i]

        return prec_at_cutoff, rec_at_cutoff, f_at_cutoff

    def calculate_r_precision(self, query, rq, num_ret, num_rel_ret, prec_list):
        if rq > num_ret:
            r_prec = float(num_rel_ret) / rq
        else:
            r_prec = prec_list[rq]
            
        self.r_precision_map[query] = r_prec
        return r_prec

    def write_prec_recall_file(self, query, rec_list, prec_inter_list):
        prec_at_recall = []
        i = 1
        for recall in self.recalls:
            while i <= self.max and rec_list[i] < recall:
                i += 1
            if i <= self.max:
                prec_at_recall.append(prec_inter_list[i])
            else:
                prec_at_recall.append(0)
                
        output = OUTPATH + query
        fh = open(output, "w")
        for i in range(len(self.recalls)):
            fh.write('%f\t%f\n'%(self.recalls[i], prec_at_recall[i]))
        fh.close()

    def print_all(self, tot_num_ret, tot_num_rel_ret, tot_num_rel):
        query_id = len(self.rank)
        r_prec = sum(self.r_precision_map.values()) / query_id
        avg_prec = sum(self.avg_precision_map.values()) / query_id
        ndcg = sum(self.ndcg_map.values()) / query_id
        prec = []
        recall = []
        f_measure = []
        
        for i in range(len(self.cutoffs)):
            prec_avg = self.sum_prec_at_cutoff[i] / query_id
            recall_avg = self.sum_rec_at_cutoff[i] / query_id
            f_avg = self.sum_f_at_cutoff[i] / query_id
            prec.append(prec_avg)
            recall.append(recall_avg)
            f_measure.append(f_avg)
            
        self.print_to_screen(query_id, tot_num_ret, tot_num_rel,
                             tot_num_rel_ret, r_prec, avg_prec, ndcg,
                             prec, recall, f_measure)


    def print_to_screen(self, query_id, num_ret, rq, num_rel_ret, r_prec,
                        avg_prec, ndcg, prec, recall, f_measure ):
        
        print "\nQueryid (Num):    %5d"%query_id
        print "Total number of documents over all queries"
        print "    Retrieved:    %5d"%num_ret
        print "    Relevant:     %5d"%rq
        print "    Rel_ret:      %5d"%num_rel_ret
        print "R-Precision (precision after R (= num_rel for a query) docs retrieved):"
        print "    Exact:        %.4f"%r_prec
        print "Average precision (non-interpolated) for all rel docs(averaged over queries)"
        print "                  %.4f"%avg_prec
        print "nDCG normalized with the DCG of sorted list"
        print "                  %.4f"%ndcg
        print "Precision:"
        print "  At    5 docs:   %.4f"%prec[0]
        print "  At   10 docs:   %.4f"%prec[1]
        print "  At   20 docs:   %.4f"%prec[2]
        print "  At   50 docs:   %.4f"%prec[3]
        print "  At  100 docs:   %.4f"%prec[4]
        print "Recall:"
        print "  At    5 docs:   %.4f"%recall[0]
        print "  At   10 docs:   %.4f"%recall[1]
        print "  At   20 docs:   %.4f"%recall[2]
        print "  At   50 docs:   %.4f"%recall[3]
        print "  At  100 docs:   %.4f"%recall[4]
        print "F-measure:"
        print "  At    5 docs:   %.4f"%f_measure[0]
        print "  At   10 docs:   %.4f"%f_measure[1]
        print "  At   20 docs:   %.4f"%f_measure[2]
        print "  At   50 docs:   %.4f"%f_measure[3]
        print "  At  100 docs:   %.4f"%f_measure[4]


def main(argv):
    argv1 = QREL_PATH_HW1
    argv2 = RANK_PATH_HW1
##    argv1 = QREL_PATH_HW5
##    argv2 = RANK_PATH_HW5
    output_all = False

    trec = TrecEval(argv1, argv2, output_all)
    trec.trec_models()

if __name__ == '__main__':
    main(sys.argv)
